from django.db import models, transaction
from django.utils import timezone
from django.template.defaultfilters import slugify
from polymorphic.models import PolymorphicModel

from somatic_variant_db.settings import (
    BASE_DIR,
    SVIG_CODE_VERSION,
    BIOLOGICAL_CLASS_CHOICES,
    CLINICAL_CLASS_CHOICES,
    CODE_PRETTY_PRINT,
    CODE_SCORES,
)

import yaml
import os
from collections import OrderedDict

from analysis.models import VariantInstance
from swgs.models import GermlineVariantInstance, SomaticVariantInstance


## TODO Variant models - these need overhaul


class AnnotationVersions(models.Model):
    version = models.IntegerField(primary_key=True)
    vep_version = models.IntegerField()
    cgc_version = models.CharField(max_length=20)
    gnomad_version = models.CharField(max_length=20)


class Variant(models.Model):
    svd_variant = models.ForeignKey(
        "analysis.VariantPanelAnalysis", on_delete=models.CASCADE
    )
    # TODO can have seperate links here for e.g. SWGS variants/ manually added variants
    vep_csq = models.CharField(max_length=20)
    cgc_mode_action = models.CharField(max_length=20)
    cgc_mutation_types = models.CharField(max_length=20)
    annotation_versions = models.ForeignKey(
        "AnnotationVersions", on_delete=models.CASCADE
    )

    def __str__(self):
        gene = self.svd_variant.variant_instance.gene
        hgvs_c = self.svd_variant.variant_instance.hgvs_c
        return f"{gene} {hgvs_c}"

    def get_variant_info(self):
        """get variant specific variables"""
        build = self.svd_variant.variant_instance.variant.genome_build
        variant_info = {
            "genomic": self.svd_variant.variant_instance.variant.variant,
            "build": build,
            "hgvs_c": self.svd_variant.variant_instance.hgvs_c,
            "hgvs_p": self.svd_variant.variant_instance.hgvs_p,
            "gene": self.svd_variant.variant_instance.gene,
            "exon": self.svd_variant.variant_instance.exon,
            "consequence": self.vep_csq,
            "mode_action": self.cgc_mode_action,
            "mutation_types": self.cgc_mutation_types,
            "annotation_versions": self.annotation_versions,
        }
        return variant_info

    def get_sample_info(self):
        sample_info = {
            "sample_id": self.svd_variant.sample_analysis.sample.sample_id,
            "worksheet_id": self.svd_variant.sample_analysis.worksheet.ws_id,
            "svd_panel": self.svd_variant.sample_analysis.panel,
        }
        return sample_info

    def get_canonical_gene_variants(self):
        canonical_variants = CanonicalList.objects.filter(
            gene=self.svd_variant.variant_instance.gene
        )
        l = []
        matching = self.get_canonical_exact_match()
        for c in canonical_variants:
            temp_dict = {
                "hgvs_c": c.hgvs_c,
                "hgvs_p": c.hgvs_p,
                "match": c == matching,
            }
            l.append(temp_dict)
        return l

    def get_canonical_exact_match(self):
        try:
            c = CanonicalList.objects.filter(variants=self.pk).latest("pk")
            return c
        except:
            return False

    def get_previous_classifications(self):
        """get all previous classifications of a variant"""
        return {
            "gene_canonical_list": self.get_canonical_gene_variants(),
            "canonical_match": self.get_canonical_exact_match(),
        }
        # get all previous classifications
        # check canonical list - how is this stored?
        # check same tumour type
        # check all others


class CanonicalList(models.Model):
    """TODO this will need redoing"""

    gene = models.CharField(max_length=20, null=True, blank=True)
    tumour_type = models.CharField(max_length=20, null=True, blank=True)
    hgvs_c = models.CharField(max_length=50, null=True, blank=True)
    hgvs_p = models.CharField(max_length=50, null=True, blank=True)
    variants = models.ManyToManyField(
        "Variant", blank=True, related_name="canonical_list"
    )  # TODO this is actually more like a variant instance, should be specific variant

    def contains_variant(self, variant):
        return self.objects.filter(variants__id=variant)


# manual variant
# training variant lists


## Classification models


class Classification(models.Model):
    """
    A classification of a single variant

    """

    svig_version = models.CharField(max_length=20)
    variant = models.ForeignKey("Variant", on_delete=models.CASCADE)
    full_classification = models.BooleanField(default=False)
    previous_classification = models.ForeignKey(
        "Variant",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="previous_classification_used",
    )
    final_biological_class = models.CharField(
        max_length=2, choices=BIOLOGICAL_CLASS_CHOICES, blank=True, null=True
    )
    final_biological_score = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"#{self.pk} - {self.variant}"

    def get_sample_info(self):
        sample_info = self.variant.get_sample_info()
        sample_info["specific_tumour_type"] = (
            "MDS"  # TODO where will this come from? hopefully analysis app
        )
        return sample_info

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

    def get_all_checks(self):
        return Check.objects.filter(classification=self).order_by("pk")

    def get_dropdown_options(self, code_list):
        """get all dropdown options for a list of codes TODO can simplify"""
        config_file = os.path.join(
            BASE_DIR, f"svig/config/svig_{SVIG_CODE_VERSION}.yaml"
        )
        with open(config_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        code_info = config["codes"]

        dropdown_options = [
            {"value": "|".join([f"{c}_PE" for c in code_list]), "text": "Pending"},
            {"value": "|".join([f"{c}_NA" for c in code_list]), "text": "Not applied"},
        ]
        if len(code_list) > 2:
            raise ValueError("max number of combined codes is 2")

        elif len(code_list) == 1:
            for option in code_info[code_list[0]]["options"]:
                text = f"{code_list[0]} {CODE_PRETTY_PRINT[option]}"
                if code_list[0][0] == "B":
                    text += f" (-{CODE_SCORES[option]})"
                elif code_list[0][0] == "O":
                    text += f" (+{CODE_SCORES[option]})"
                dropdown_options.append(
                    {
                        "value": f"{code_list[0]}_{option}",
                        "text": text,
                    }
                )
        else:
            code_1, code_2 = code_list
            for option in code_info[code_1]["options"]:
                text = f"{code_1} {CODE_PRETTY_PRINT[option]}"
                if code_1[0] == "B":
                    text += f" (-{CODE_SCORES[option]})"
                elif code_1[0] == "O":
                    text += f" (+{CODE_SCORES[option]})"
                dropdown_options.append(
                    {
                        "value": f"{code_1}_{option}|{code_2}_NA",
                        "text": text,
                    }
                )
            for option in code_info[code_2]["options"]:
                text = f"{code_2} {CODE_PRETTY_PRINT[option]}"
                if code_2[0] == "B":
                    text += f" (-{CODE_SCORES[option]})"
                elif code_2[0] == "O":
                    text += f" (+{CODE_SCORES[option]})"
                dropdown_options.append(
                    {
                        "value": f"{code_1}_NA|{code_2}_{option}",
                        "text": text,
                    }
                )
        return dropdown_options

    def get_dropdown_value(self, code_list):
        latest_code_objects = self.get_latest_check().get_codes()
        l = []
        for c in code_list:
            l.append(latest_code_objects.get(code=c).get_code())
        return "|".join(l)

    def get_codes_by_category(self):
        """ordered list of codes for displaying template TODO split up more"""

        config_file = os.path.join(
            BASE_DIR, f"svig/config/svig_{SVIG_CODE_VERSION}.yaml"
        )
        with open(config_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        code_info = config["codes"]
        order_info = config["order"]

        latest_code_objects = self.get_latest_check().get_codes()

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
                    code_object = latest_code_objects.get(code=c)

                    # add detailed code description to dict
                    code_details.append({c: code_info[c]})
                    annotations += code_info[c]["annotations"]

                    # get info on what codes have been applied
                    if code_object.applied:
                        svig_codes[section]["applied_codes"].append(
                            f"{c}_{code_object.applied_strength}"
                        )
                    if code_object.pending:
                        svig_codes[section]["complete"] = False

                all_checks = []
                if len(code_list) == 1:
                    # all checks for dropdown
                    for c in all_check_objects:
                        check_code_objects = c.get_codes()
                        all_checks.append(
                            check_code_objects.get(code=code_list[0]).get_string()
                        )

                else:
                    code_1, code_2 = code_list
                    # all checks
                    for c in all_check_objects:
                        check_code_objects = c.get_codes()
                        code_1_display = check_code_objects.get(
                            code=code_1
                        ).get_string()
                        code_2_display = check_code_objects.get(
                            code=code_2
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

    def get_previous_checks(self):
        return self.get_all_checks().order_by("-pk")[1:]

    def get_latest_check(self):
        return self.get_all_checks().order_by("-pk")[0]

    def get_status(self):
        if self.get_latest_check().check_complete:
            return "Complete"
        else:
            num_checks = self.get_all_checks().count()
            return f"S-VIG check {num_checks}"

    def get_previous_classification_choices(self):
        canonical_variant = self.variant.get_canonical_exact_match()
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


class Check(models.Model):
    """
    A check of a classification
    """

    classification = models.ForeignKey("Classification", on_delete=models.CASCADE)
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
    final_biological_class = models.CharField(
        max_length=2, choices=BIOLOGICAL_CLASS_CHOICES, blank=True, null=True
    )
    final_biological_score = models.IntegerField(blank=True, null=True)
    final_clinical_class = models.CharField(
        max_length=2, choices=CLINICAL_CLASS_CHOICES, blank=True, null=True
    )
    reporting_comment = models.CharField(max_length=500, blank=True, null=True)

    def get_codes(self):
        """get all classification codes for the current check"""
        return CodeAnswer.objects.filter(check_object=self)

    def update_classification(self):
        """calculate the current score and biological classification"""
        score_counter = 0

        codes = self.get_codes()
        for c in codes:
            if c.applied:
                code_type = c.get_code_type()
                if code_type == "Benign":
                    score_counter -= CODE_SCORES[c.applied_strength]
                elif code_type == "Oncogenic":
                    score_counter += CODE_SCORES[c.applied_strength]

        # work out class from score counter
        class_list = OrderedDict(
            {
                "Likely benign": -6,
                "VUS": 0,
                "Likely oncogenic": 6,
                "Oncogenic": 10,
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
        code_objects = self.get_codes()
        for s in selections:

            # get specific code & type
            c, value = s.split("_")
            code_obj = code_objects.get(code=c)
            code_type = code_obj.get_code_type()

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
                strength = value

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
        self.final_biological_class = None
        self.final_biological_score = None
        self.final_clinical_class = None
        self.save()

    @transaction.atomic
    def create_code_answers(self):
        """make a set of code answers against the current check"""
        # load in list of S-VIG codes from yaml
        config_file = os.path.join(
            BASE_DIR, f"svig/config/svig_{SVIG_CODE_VERSION}.yaml"
        )
        with open(config_file) as f:
            svig_codes = yaml.load(f, Loader=yaml.FullLoader)

        # loop through the codes and make code answer objects
        for code in svig_codes["codes"]:
            CodeAnswer.objects.create(code=code, check_object=self)

    @transaction.atomic
    def delete_code_answers(self):
        """remove the set of code answers for the current check"""
        codes = self.get_codes()
        for c in codes:
            c.delete()


class CodeAnswer(models.Model):
    """
    A check of an individual code

    """

    code = models.CharField(max_length=20)
    check_object = models.ForeignKey("Check", on_delete=models.CASCADE)
    pending = models.BooleanField(default=True)
    applied = models.BooleanField(default=False)
    applied_strength = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.get_code()}"

    def get_code(self):
        if self.pending:
            return f"{self.code}_PE"
        elif self.applied:
            return f"{self.code}_{self.applied_strength}"
        else:
            return f"{self.code}_NA"

    def get_code_type(self):
        if self.code[0] == "B":
            return "Benign"
        elif self.code[0] == "O":
            return "Oncogenic"

    def pretty_print_code(self):
        return CODE_PRETTY_PRINT[self.applied_strength]

    def get_score(self):
        if self.get_code_type() == "Benign":
            score = f"-{CODE_SCORES[self.applied_strength]}"
        elif self.get_code_type() == "Oncogenic":
            score = f"+{CODE_SCORES[self.applied_strength]}"

    def get_string(self):
        if self.pending:
            return "Pending"
        elif self.applied:
            return f"{self.code} {self.pretty_print_code()} ({self.get_score()})"
        else:
            return "Not applied"


class AbstractComment(models.Model):
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

    details = models.CharField(max_length=500)


# UPDATED MODELS FOR CLASSIFYING please change as needed

class Guideline(models.Model):
    """
    Model to store which guidelines are being used
    """
    guideline = models.CharField(max_length=200, unique=True)
    criteria = models.ManyToManyField("ClassificationCriteria", related_name="guideline")
    sort_order = models.CharField(max_length=200)

    def __str__(self):
        return self.guideline
    
class ClassificationCriteriaStrength(models.Model):
    """
    Strengths at which the criteria can be applied at
    """
    id = models.AutoField(primary_key=True)
    strength = models.CharField(max_length=20)
    evidence_points = models.IntegerField()

    class Meta:
        unique_together = ["strength", "evidence_points"]

    def __str__(self):
        return f"{self.strength} {str(self.evidence_points)}"

class ClassificationCriteriaCode(models.Model):
    """
    Codes that can be applied
    """
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)
    pathogenic_or_benign = models.CharField(max_length=1)
    description = models.TextField(null=True, blank=True)
    links = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.code

class ClassificationCriteria(models.Model):
    """
    All available combinations of codes and strengths
    """
    id = models.AutoField(primary_key=True)
    code = models.ForeignKey("ClassificationCriteriaCode", on_delete=models.CASCADE)
    strength = models.ForeignKey("ClassificationCriteriaStrength", on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ["code", "strength"]

    def form_display(self):
        return f"{self.code.code}_{self.strength.strength}"
    
class ClassifyVariant(models.Model):
    """
    A given variant for a given transcript
    This is some duplication of information that's stored elsewhere but will make this app easier to work with
    We can populate based on existing models to continue data integrity
    """
    hgvsc = models.CharField(max_length=200, unique=True)
    hgvsp = models.CharField(max_length=200, null=True, blank=True)
    b38_coords = models.CharField(max_length=200)
    b37_coords = models.CharField(max_length=200) #autopopulate with variantvalidator? otherwise we have to make these both nullable

class ClassifyVariantInstance(PolymorphicModel):
    """
    Top level model for variant instance to account for all the SVD apps and manual variants added directly to classify
    """
    variant = models.ForeignKey("ClassifyVariant", on_delete=models.CASCADE)

class AnalysisVariantInstance(ClassifyVariantInstance):
    """
    Links out to the analysis app (TSO500, ctDNA, CRM, BRCA)
    """
    variant_instance = models.ForeignKey(VariantInstance, on_delete=models.CASCADE)

class SWGSGermlineVariantInstance(ClassifyVariantInstance):
    """
    Germline variants from the SWGS app
    """
    variant_instance = models.ForeignKey(GermlineVariantInstance, on_delete=models.CASCADE)

class SWGSSomaticVaraintInstance(ClassifyVariantInstance):
    """
    Somatic variants from the SWGS app
    """
    variant_instance = models.ForeignKey(SomaticVariantInstance, on_delete=models.CASCADE)

class ManualVariantInstance(ClassifyVariantInstance):
    """
    Variants added manually directly to classify
    """
    pass
