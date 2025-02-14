from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.template.defaultfilters import slugify
from polymorphic.models import PolymorphicModel

from somatic_variant_db.settings import BIOLOGICAL_CLASS_CHOICES

import yaml
import os
from collections import OrderedDict

from analysis.models import VariantPanelAnalysis
from swgs.models import GermlineVariantInstance, SomaticVariantInstance


class Guideline(models.Model):
    """
    Model to store which guidelines are being used
    """
    guideline = models.CharField(max_length=200, unique=True)
    criteria = models.ManyToManyField("ClassificationCriteria", related_name="guideline")
    sort_order = models.ManyToManyField("ClassificationCriteriaCategory", through="CategorySortOrder")

    def __str__(self):
        return self.guideline


class CategorySortOrder(models.Model):
    """
    Through model to allow for categories of codes to be sorted for each guideline
    """
    guideline = models.ForeignKey("Guideline", on_delete=models.CASCADE)
    category = models.ForeignKey("ClassificationCriteriaCategory", on_delete=models.CASCADE)
    sort_order = models.IntegerField()

    class Meta:
        unique_together = ["guideline", "category"]

    def __str__(self):
        return f"{self.guideline} {self.category} {self.sort_order}"
    
    def get_all_codes_for_category(self):
        all_codes_for_guideline = self.guideline.criteria.all().values("criteria__code__code")


class ClassificationCriteria(models.Model):
    """
    All available combinations of codes and strengths
    """
    id = models.AutoField(primary_key=True)
    code = models.ForeignKey("ClassificationCriteriaCode", on_delete=models.CASCADE, related_name="classification_criteria")
    strength = models.ForeignKey("ClassificationCriteriaStrength", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["code", "strength"]

    def __str__(self):
        return f"{self.code.code}_{self.strength.strength}"
    
    def classify_shorthand(self):
        paired_code = self.code.paired_criteria
        if paired_code is not None:
            paired_criteria = paired_code.code
            if self.code.pathogenic_or_benign == "O" or self.code.pathogenic_or_benign == "P":
                return f"{self.code}_{self.strength.shorthand}|{paired_criteria}_NA"
            elif self.code.pathogenic_or_benign == "B":
                return f"{paired_criteria}_NA|{self.code}_{self.strength.shorthand}"
        else:
            return f"{self.code}_{self.strength.shorthand}"
    
    def pretty_print(self):
        if self.strength.evidence_points > 0:
            evidence_points = f"+{self.strength.evidence_points}"
        else:
            evidence_points = self.strength.evidence_points
        return f"{self.code.code} {self.strength.pretty_print()} ({evidence_points})"


class ClassificationCriteriaCategory(models.Model):
    """
    Categories that the codes belong to - used to group codes for display
    """
    category = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.category}"
    
    def pretty_print(self):
        return self.category.title().replace("_", " ")


class ClassificationCriteriaCode(models.Model):
    """
    Codes that can be applied
    """
    code = models.CharField(max_length=10, unique=True)
    pathogenic_or_benign = models.CharField(max_length=1)
    description = models.TextField(null=True, blank=True)
    links = models.TextField(null=True, blank=True)
    category = models.ForeignKey("ClassificationCriteriaCategory", on_delete=models.CASCADE)
    paired_criteria = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.code


class ClassificationCriteriaStrength(models.Model):
    """
    Strengths at which the criteria can be applied at
    """
    strength = models.CharField(max_length=20)
    shorthand = models.CharField(max_length=2)
    evidence_points = models.IntegerField()

    class Meta:
        unique_together = ["strength", "evidence_points"]

    def __str__(self):
        return f"{self.strength} {str(self.evidence_points)}"

    def pretty_print(self):
        return self.strength.title().replace("_", " ")


class ClassifyVariant(models.Model):
    """
    A given variant for a given transcript
    This is some duplication of information that's stored elsewhere but will make this app easier to work with
    We can populate based on existing models to continue data integrity
    """
    hgvs_c = models.CharField(max_length=200, unique=True)
    hgvs_p = models.CharField(max_length=200, null=True, blank=True)
    b38_coords = models.CharField(max_length=200)
    b37_coords = models.CharField(max_length=200) #autopopulate with variantvalidator? otherwise we have to make these both nullable

    def __str__(self):
        return self.hgvs_c

    def get_variant_info(self):
        """ get variant specific variables """
        variant_info = {
            "genomic": self.b38_coords,
            "build": "TODO",
            "hgvs_c": self.hgvs_c,
            "hgvs_p": self.hgvs_p,
            "gene": "TODO",
            "exon": "TODO",
        }
        return variant_info

    def get_previous_classifications(self):
        """ get all previous classifications of a variant """
        # TODO this is hardcoded
        return {
            "gene_canonical_list": [],
            "canonical_match": [],
        }


class ClassifyVariantInstance(PolymorphicModel):
    """
    Top level model for variant instance to account for all the SVD apps and manual variants added directly to classify
    """
    variant = models.ForeignKey("ClassifyVariant", on_delete=models.CASCADE)
    guideline = models.ForeignKey("Guideline", on_delete=models.CASCADE)

    def __str__(self):
        return f"#{self.pk} - {self.variant.hgvs_c}"

    def get_all_checks(self):
        return Check.objects.filter(classification=self).order_by("pk")

    def get_previous_checks(self):
        return self.get_all_checks().order_by("-pk")[1:]

    def get_latest_check(self):
        return self.get_all_checks().order_by("-pk")[0]

    def get_status(self):
        if self.get_latest_check().check_complete:
            return "Complete"
        else:
            num_checks = self.get_all_checks().count()
            return f"Check {num_checks}"

    def get_classification_info(self):
        current_check_obj = self.get_latest_check()
        classification_info = {
            "classification_obj": self,
            "current_check": current_check_obj,
            "all_checks": self.get_all_checks(),
        }
        if current_check_obj.full_classification:
            current_score, current_class = current_check_obj.update_classification()
            classification_info["codes_by_category"] = self.get_codes_by_category()
            classification_info["current_class"] = current_class
            classification_info["current_score"] = current_score
        return classification_info

    def get_dropdown_options(self, code_list):
        """get all dropdown options for a list of codes"""

        # we're only expecting up to 2 paired codes
        if len(code_list) > 2:
            raise ValueError("max number of combined codes is 2")

        # create pending and not applied options
        dropdown_options = [
            {"value": "|".join([f"{c}_PE" for c in code_list]), "text": "Pending"},
            {"value": "|".join([f"{c}_NA" for c in code_list]), "text": "Not applied"},
        ]

        for code in code_list:
            all_strengths = self.guideline.criteria.filter(code__code=code)
            for strength in all_strengths:
                value = strength.classify_shorthand()
                text = strength.pretty_print()
                dropdown_options.append(
                    {"value": value, "text": text}
                )

        return dropdown_options


    def get_dropdown_value(self, code_list):
        latest_code_objects = self.get_latest_check().get_code_answers()
        l = []
        for c in code_list:
            l.append(latest_code_objects.get(code__code=c).get_code())
        return "|".join(l)


    def get_codes_by_category(self):
        """ordered list of codes for displaying template"""
        # TODO remove SVIG specifics and simplify

        order_info = self.get_order_info()
        code_info = self.get_code_info()

        latest_code_objects = self.get_latest_check().get_code_answers()

        all_check_objects = self.get_all_checks()

        svig_codes = {}
        for section, codes in order_info.items():
            svig_codes[section] = {
                "slug": slugify(section),
                "codes": {},
                "applied_codes": [],
                "complete": True,
            }
            for code in codes:
                code_list = code.split("_")

                # loop through each code and extract info
                code_details = []
                annotations = []

                for c in code_list:
                    # get applied codes
                    code_object = latest_code_objects.get(code__code=c)

                    # add detailed code description to dict
                    code_details.append({c: code_info[c]})
                    annotations += code_info[c]["annotations"]

                    # get info on what codes have been applied
                    if code_object.applied:
                        svig_codes[section]["applied_codes"].append(
                            f"{c}_{code_object.applied_strength.shorthand}"
                        )
                    if code_object.pending:
                        svig_codes[section]["complete"] = False

                all_checks = []
                if len(code_list) == 1:
                    # all checks for dropdown
                    for c in all_check_objects:
                        check_code_objects = c.get_code_answers()
                        all_checks.append(
                            check_code_objects.get(code__code=code_list[0]).get_string()
                        )

                else:
                    code_1, code_2 = code_list
                    # all checks
                    for c in all_check_objects:
                        check_code_objects = c.get_code_answers()
                        code_1_display = check_code_objects.get(
                            code__code=code_1
                        ).get_string()
                        code_2_display = check_code_objects.get(
                            code__code=code_2
                        ).get_string()

                        if code_1_display == code_2_display:
                            all_checks.append(code_1_display)
                        else:
                            if code_1_display == "Not applied":
                                all_checks.append(code_2_display)

                            elif code_2_display == "Not applied":
                                all_checks.append(code_1_display)

                # remove duplicates (template doesnt like sets so convert back to list)
                annotations = list(set(annotations))
                # add all to final dict
                svig_codes[section]["codes"][code] = {
                    "list": code_list,
                    "details": code_details,
                    "dropdown": self.get_dropdown_options(code_list),
                    "value": self.get_dropdown_value(code_list),
                    "annotations": annotations,
                    "all_checks": all_checks,
                }
        return svig_codes

    def get_order_info(self):
        """Get the ordered list of codes dictionary for the ajax"""

        order_info = {}

        sort_order_query = self.guideline.sort_order.all().order_by("categorysortorder__sort_order")
        
        for sort_order in sort_order_query:
            pretty_print = sort_order.pretty_print()
            code_list = []
            codes = ClassificationCriteriaCode.objects.filter(
                Q(category=sort_order) &
                Q(classification_criteria__guideline=self.guideline)
            ).distinct()

            for code in codes:
                if code.paired_criteria is not None:
                    # some germline codes are multiple pathogenic options
                    if code.pathogenic_or_benign == "P" and code.paired_criteria.pathogenic_or_benign == "P":
                        codes_for_string = [code.code, code.paired_criteria.code]
                        codes_for_string.sort()
                        code_string = f"{codes_for_string[0]}_{codes_for_string[1]}"
                    elif code.pathogenic_or_benign == "O" or code.pathogenic_or_benign == "P":
                        code_string = f"{code.code}_{code.paired_criteria.code}"
                    elif code.pathogenic_or_benign == "B":
                        code_string = f"{code.paired_criteria.code}_{code.code}"
                else:
                    code_string = code.code
                code_list.append(code_string)

            code_list = list(set(code_list))
            code_list.sort()
            order_info[pretty_print] = code_list

        return order_info
    
    def get_code_info(self):
        """Get the code information dictionary for the ajax"""

        type_dict = {
            "O": "oncogenic",
            "P": "pathogenic",
            "B": "benign"
        }

        codes_dict = {}
        codes = self.guideline.criteria.all()
        for code in codes:

            code_name = code.code.code
            type = type_dict[code.code.pathogenic_or_benign]
            category = code.code.category.category
            options = code.strength.shorthand
            description = code.code.description
            annotations = []

            try:
                codes_dict[code_name]["options"].append(options)
            except KeyError:
                codes_dict[code_name] = {
                    "type": type,
                    "category": category,
                    "options": [options],
                    "description": description,
                    "annotations": annotations
                }
            
        return codes_dict

    
    def get_previous_classification_choices(self):
        canonical_variant = False # TODO these are hardcoded
        previous_classification = False  # TODO
        if canonical_variant:
            return (
                (
                    "canonical",
                    f"Confirm selected canonical variant - {canonical_variant.hgvs_p}",
                ),
            )
        elif previous_classification:
            return (
                ("previous", f"Use selected previous classification - ???"),
                ("new", "Perform full classification"),
            )
        else:
            return (("new", "Perform full classification"),)

    def make_new_check(self):
        new_check = Check.objects.create(classification=self)

    @transaction.atomic
    def signoff_check(self, current_check, next_step):
        """complete a whole check"""
        if next_step == "C":
            previous_checks = self.get_previous_checks()
            if not previous_checks.exists():
                return False, "Cannot complete analysis, two checks required"

        elif next_step == "B":
            previous_checks = self.get_previous_checks()
            if previous_checks.exists():
                previous_check = previous_checks[0]
                previous_check.reopen_check()
                current_check.delete()
                return True, previous_check
            else:
                return False, "Cannot send back, this is the first check"

        else:
            current_check.check_complete = True
            current_check.signoff_time = timezone.now()
            current_check.save()

            if next_step == "E":
                self.make_new_check()
            # TODO save results to classification obj if final check

            return True, None


class AnalysisVariantInstance(ClassifyVariantInstance):
    """
    Links out to the analysis app (TSO500, ctDNA, CRM, BRCA)
    """
    variant_instance = models.ForeignKey(VariantPanelAnalysis, on_delete=models.CASCADE)

    def get_sample_info(self):
        sample_info = {
            "sample_id": self.variant_instance.sample_analysis.sample.sample_id,
            "worksheet_id": self.variant_instance.sample_analysis.worksheet.ws_id,
            "svd_panel": self.variant_instance.sample_analysis.panel,
            "specific_tumour_type": "TODO",
        }
        return sample_info


class SWGSGermlineVariantInstance(ClassifyVariantInstance):
    """
    Germline variants from the SWGS app
    """
    variant_instance = models.ForeignKey(GermlineVariantInstance, on_delete=models.CASCADE)

    def get_sample_info(self):
        # TODO - these will need coding relative to SWGS app
        sample_info = {
            "sample_id": "TODO",
            "worksheet_id": "TODO",
            "svd_panel": "TODO",
            "specific_tumour_type": "TODO",
        }
        return sample_info


class SWGSSomaticVaraintInstance(ClassifyVariantInstance):
    """
    Somatic variants from the SWGS app
    """
    variant_instance = models.ForeignKey(SomaticVariantInstance, on_delete=models.CASCADE)

    def get_sample_info(self):
        # TODO - these will need coding relative to SWGS app
        sample_info = {
            "sample_id": "TODO",
            "worksheet_id": "TODO",
            "svd_panel": "TODO",
            "specific_tumour_type": "TODO",
        }
        return sample_info


class ManualVariantInstance(ClassifyVariantInstance):
    """
    Variants added manually directly to classify
    """
    pass


class Check(models.Model):
    """
    A check of a classification
    # TODO choices are linked to SVIG
    """
    classification = models.ForeignKey("ClassifyVariantInstance", on_delete=models.CASCADE)
    info_check = models.BooleanField(default=False)
    previous_classifications_check = models.BooleanField(default=False)
    svig_check = models.BooleanField(default=False)
    full_classification = models.BooleanField(default=False)
    check_complete = models.BooleanField(default=False)
    signoff_time = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="svig_checker",
    )
    final_class = models.CharField(
        max_length=2, choices=BIOLOGICAL_CLASS_CHOICES, blank=True, null=True
    )
    final_score = models.IntegerField(blank=True, null=True)
    reporting_comment = models.CharField(max_length=500, blank=True, null=True) # TODO not being used, might move somewhere else

    def get_code_answers(self):
        """get all classification codes for the current check"""
        return CodeAnswer.objects.filter(check_object=self)

    def update_classification(self):
        """calculate the current score and classification"""
        score_counter = 0
        codes = self.get_code_answers()
        for c in codes:
            if c.applied:
                score_counter += c.applied_strength.evidence_points

        #TODO this needs moving somewhere more modelly
        # work out class from score counter
        if self.classification.guideline.guideline == "svig_2024":
            class_list = OrderedDict(
                {
                    "Likely benign": -6,
                    "VUS": 0,
                    "Likely oncogenic": 6,
                    "Oncogenic": 10,
                }
            )
        elif self.classification.guideline.guideline == "acgs_2024":
            class_list = OrderedDict(
                {
                    "Likely benign": -6,
                    "VUS cold": 0,
                    "VUS warm": 2,
                    "VUS hot": 4,
                    "Likely pathogenic": 6,
                    "Pathogenic": 10
                }
            )

        # loop through in order until the score no longer meets the threshold
        classification = "Benign"
        for c, score in class_list.items():
            if score_counter >= score:
                classification = c

        return score_counter, classification

    @transaction.atomic
    def update_codes(self, selections):
        """update each code answer and then work out overall score/ class"""

        # load all code answer objects & loop through each selection
        code_objects = self.get_code_answers()
        for s in selections:

            # get specific code & type
            c, value = s.split("_")
            code_obj = code_objects.get(code__code=c)

            # if check pending, set pending to true
            if value == "PE":
                pending = True
                applied = False
                strength = None

            # if code not applied, set pending & applied to false
            elif value == "NA":
                pending = False
                applied = False
                strength = None

            # if code applied, save to models
            else:
                pending = False
                applied = True
                criteria_strength_obj = ClassificationCriteria.objects.get(code=code_obj.code, strength__shorthand=value)
                strength = criteria_strength_obj.strength

            # save values to database
            code_obj.pending = pending
            code_obj.applied = applied
            code_obj.applied_strength = strength
            code_obj.save()

        return True

    @transaction.atomic
    def reopen_check(self):
        """reopen a completed check"""
        self.check_complete = False
        self.signoff_time = None
        self.save()

    @transaction.atomic
    def reopen_info_tab(self):
        """reset variant tab, calls other reset functions to reset other two tabs"""
        self.info_check = False
        self.reopen_previous_class_tab()

    @transaction.atomic
    def reopen_previous_class_tab(self):
        """reset previous classifications tab, calls svig function to reset svig tab"""
        self.previous_classifications_check = False
        self.full_classification = False
        self.reopen_svig_tab()
        self.delete_code_answers()

    @transaction.atomic
    def reopen_svig_tab(self):
        """reset the svig tab"""
        self.svig_check = False
        self.final_score = None
        self.final_class = None
        self.save()


    @transaction.atomic
    def create_code_answers(self):
        """make a set of code answers against the current check"""

        all_codes_query = self.classification.guideline.criteria.all()
        all_codes = [code.code.code for code in all_codes_query]
        all_codes = list(set(all_codes))

        for code in all_codes:
            code_obj = ClassificationCriteriaCode.objects.get(code=code)
            CodeAnswer.objects.create(code=code_obj, check_object=self)

    @transaction.atomic
    def delete_code_answers(self):
        """remove the set of code answers for the current check"""
        codes = self.get_code_answers()
        for c in codes:
            c.delete()


class CodeAnswer(models.Model):
    """
    A check of an individual code

    """
    code = models.ForeignKey("ClassificationCriteriaCode", on_delete=models.CASCADE)
    check_object = models.ForeignKey("Check", on_delete=models.CASCADE)
    pending = models.BooleanField(default=True)
    applied = models.BooleanField(default=False)
    applied_strength = models.ForeignKey("ClassificationCriteriaStrength", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.get_code()}"

    def get_code(self):
        if self.pending:
            return f"{self.code.code}_PE"
        elif self.applied:
            return f"{self.code.code}_{self.applied_strength.shorthand}"
        else:
            return f"{self.code.code}_NA"

    def get_code_type(self):
        if self.code.pathogenic_or_benign == "B":
            return "Benign"
        elif self.code.pathogenic_or_benign == "O":
            return "Oncogenic"
        elif self.code.pathogenic_or_benign == "P":
            return "Pathogenic"

    def pretty_print_code(self):
        return self.code.code

    def get_score(self):
        # TODO SVIG specific
        if self.get_code_type() == "Benign":
            score = f"{self.applied_strength.evidence_points}"
        elif self.get_code_type() == "Oncogenic":
            score = f"+{self.applied_strength.evidence_points}"

    def get_string(self):
        if self.pending:
            return "Pending"
        elif self.applied:
            return f"{self.code} {self.pretty_print_code()} ({self.get_score()})"
        else:
            return "Not applied"


'''class AbstractComment(models.Model):
    """general comment model"""

    classification = models.ForeignKey("Classification", on_delete=models.CASCADE)
    time = models.DateTimeField()
    comment = models.CharField(max_length=500)


class CodeComment(AbstractComment):
    """comment on a specifc code"""

    check_obj = models.ForeignKey(
        "Check", on_delete=models.CASCADE, related_name="code_comments"
    )
    code = models.ForeignKey("CodeAnswer", on_delete=models.CASCADE)


class GeneralComment(AbstractComment):
    """general comment on a check"""

    check_obj = models.ForeignKey(
        "Check", on_delete=models.CASCADE, related_name="general_comments"
    )


class SystemComment(AbstractComment):
    """system comment for audit trail"""

    details = models.CharField(max_length=500)'''
