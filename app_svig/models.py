from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify

from somatic_variant_db.settings import BASE_DIR, SVIG_CODE_VERSION

import yaml
import os
from collections import OrderedDict


class AnnotationVersions(models.Model):
    version = models.IntegerField(primary_key=True)
    vep_version = models.IntegerField()
    cgc_version = models.CharField(max_length=20)
    gnomad_version = models.CharField(max_length=20)


class Variant(models.Model):
    svd_variant = models.ForeignKey('analysis.VariantPanelAnalysis', on_delete=models.CASCADE)
    # TODO can have seperate links here for e.g. SWGS variants/ manually added variants
    vep_csq = models.CharField(max_length=20)
    cgc_mode_action = models.CharField(max_length=20)
    cgc_mutation_types = models.CharField(max_length=20)
    annotation_versions = models.ForeignKey('AnnotationVersions', on_delete=models.CASCADE)

    def __str__(self):
        return self.svd_variant.variant_instance.gene + ' ' + self.svd_variant.variant_instance.hgvs_c

    def get_variant_info(self):
        # get variant specific variables
        build = self.svd_variant.variant_instance.variant.genome_build
        build_css_dict = {37: 'info', 38: 'success'} # TODO add to global settings file? probably used a few times
        build_css_tag = build_css_dict[build]

        variant_info = {
            'genomic': self.svd_variant.variant_instance.variant.variant,
            'build': build,
            'build_css_tag': build_css_tag,
            'hgvs_c': self.svd_variant.variant_instance.hgvs_c,
            'hgvs_p': self.svd_variant.variant_instance.hgvs_p,
            'gene': self.svd_variant.variant_instance.gene,
            'exon': self.svd_variant.variant_instance.exon,
            'consequence': self.vep_csq,
            'mode_action': self.cgc_mode_action,
            'mutation_types': self.cgc_mutation_types,
            'annotation_versions': self.annotation_versions
        }

        return variant_info

    def get_sample_info(self):
        sample_info = {
            'sample_id': self.svd_variant.sample_analysis.sample.sample_id,
            'worksheet_id':  self.svd_variant.sample_analysis.worksheet.ws_id,
            'svd_panel':  self.svd_variant.sample_analysis.panel,
        }
        return sample_info

    def get_canonical_gene_variants(self):
        canonical_variants = CanonicalList.objects.filter(gene=self.svd_variant.variant_instance.gene)
        l = []
        matching = self.get_canonical_exact_match()
        for c in canonical_variants:
            temp_dict = {
                'hgvs_c': c.hgvs_c,
                'hgvs_p': c.hgvs_p,
                'match': c == matching,
            }
            l.append(temp_dict)
        return l

    def get_canonical_exact_match(self):
        try:
            c = CanonicalList.objects.filter(variants=self.pk).latest('pk')
            return c
        except:
            return False

    def get_previous_classifications(self):
        """ get all previous classifications of a variant """
        return {
            'gene_canonical_list': self.get_canonical_gene_variants(),
            'canonical_match': self.get_canonical_exact_match(),
            }
        # get all previous classifications
        # check canonical list - how is this stored?
        # check same tumour type
        # check all others


class Classification(models.Model):
    """
    An individual classification of a single variant

    """
    variant = models.ForeignKey('Variant', on_delete=models.CASCADE)
    full_classification = models.BooleanField(default=False)
    svig_version = models.CharField(max_length=20)

    def __str__(self):
        return f'#{self.pk} - {self.variant}'

    def get_sample_info(self):
        sample_info = self.variant.get_sample_info()
        sample_info['specific_tumour_type'] = 'MDS'  # TODO where will this come from? hopefully analysis app
        return sample_info

    def get_classification_info(self):
        current_check_obj = self.get_latest_check()
        classification_info = {
            'classification_obj': self,
            'current_check': current_check_obj,
            'all_checks': self.get_all_checks(),
        }
        if current_check_obj.full_classification:
            current_score, current_class, class_css = current_check_obj.classify()
            classification_info['all_codes'] = current_check_obj.codes_to_dict()
            classification_info['codes_by_category'] = current_check_obj.codes_by_category()
            classification_info['all_applied_codes'] = self.get_all_applied_codes()
            classification_info['current_class'] = current_class
            classification_info['current_score'] = current_score
            classification_info['class_css'] = class_css
        return classification_info

    def get_context(self):
        context = {
            'sample_info': self.get_sample_info(),
            'variant_info': self.variant.get_variant_info(),
            'classification_info': self.get_classification_info(),
            'previous_classifications': self.variant.get_previous_classifications(),
        }
        return context

    def make_new_check(self):
        new_check = Check.objects.create(classification=self)

    def get_all_checks(self):
        return Check.objects.filter(classification=self).order_by('-pk')

    def get_previous_checks(self):
        return self.get_all_checks()[1:]

    def get_latest_check(self):
        return self.get_all_checks()[0]

    def get_status(self):
        if self.get_latest_check().check_complete:
            return 'Complete'
        else:
            num_checks = self.get_all_checks().count()
            return f'S-VIG check {num_checks}'

    def get_all_applied_codes(self):
        return list(reversed([c.codes_to_dict() for c in self.get_all_checks()]))

    def get_previous_classification_choices(self):
        canonical_variant = self.variant.get_canonical_exact_match()
        previous_classification = False  # TODO
        if canonical_variant:
            return (('canonical', f'Confirm selected canonical variant - {canonical_variant.hgvs_p}'), )
        elif previous_classification:
            return (('previous', f'Use selected previous classification - ???'), ('new', 'Perform full classification'), )
        else:
            return (('new', 'Perform full classification'),)


class Check(models.Model):
    """
    A check of a classification
    """
    classification = models.ForeignKey('Classification', on_delete=models.CASCADE)
    info_check = models.BooleanField(default=False)
    previous_classifications_check = models.BooleanField(default=False)
    full_classification = models.BooleanField(default=False)
    check_complete = models.BooleanField(default=False)
    signoff_time = models.DateTimeField(blank=True, null=True)
    # TODO assign user

    def make_new_codes(self):
        """
        make a set of code answers against the current check
        """
        # load in list of S-VIG codes from yaml
        config_file = os.path.join(BASE_DIR, f'app_svig/config/svig_{SVIG_CODE_VERSION}.yaml')
        with open(config_file) as f:
            svig_codes = yaml.load(f, Loader=yaml.FullLoader)

        # loop through the codes and make code answer objects
        for code in svig_codes["codes"]:
            CodeAnswer.objects.create(
                code = code,
                check_object = self
            )

    def get_codes(self, code=None):
        """
        Get all classification codes for the current check
        """
        code_objects = CodeAnswer.objects.filter(check_object=self)
        if code:
            code_objects = code_objects.get(code=code)
        return code_objects

    def remove_codes(self):
        """
        remove the set of code answers for the current check
        """
        codes = self.get_codes()
        for c in codes:
            c.delete()

    def classify(self):
        # dict of how many points per code strength, this could be in settings/svig config
        score_dict = {'SA': 100, 'VS': 8, 'ST': 4, 'MO': 2, 'SU': 1}
        score_counter = 0

        codes = self.get_codes()
        for c in codes:
            if c.applied:
                code_type = c.code[0]
                if code_type == 'B':
                    score_counter -= score_dict[c.applied_strength]
                elif code_type == 'O':
                    score_counter += score_dict[c.applied_strength]

        # work out class from score counter
        class_list = OrderedDict({
            'Likely benign': -6,
            'VUS': 0,
            'Likely oncogenic': 6,
            'Oncogenic': 10,
        })

        # loop through in order until the score no longer meets the threshold
        classification = 'Benign'
        for c, score in class_list.items():
            if score_counter >= score:
                classification = c

        # for colouring the classification display
        class_css_list = {
            'Benign': 'info',
            'Likely benign': 'info',
            'VUS': 'warning',
            'Likely oncogenic': 'danger',
            'Oncogenic': 'danger',
        }
        css_class = class_css_list[classification]

        return score_counter, classification, css_class

    def update_codes(self, selections):
        #TODO split into smaller functions

        # empty variables to store output
        selections_dict = {}
        score_counter = 0

        # dict of how many points per code strength, this could be in settings/svig config
        score_dict = {'SA': 100, 'VS': 8, 'ST': 4, 'MO': 2, 'SU': 1}

        # loop through selections and tidy up into dict
        for s in selections:
            c, v = s.split('_')

            code_type = c[0]

            if v == 'PE':
                pending = True
                applied = False
                strength = None

            elif v == 'NA':
                pending = False
                applied = False
                strength = None

            else:
                pending = False
                applied = True
                strength = v

                if code_type == 'B':
                    score_counter -= score_dict[strength]
                elif code_type == 'O':
                    score_counter += score_dict[strength]

            selections_dict[c] = {
                'pending': pending,
                'applied': applied,
                'strength': strength,
            }

        # work out class from score counter
        class_list = OrderedDict({
            'Likely benign': -6,
            'VUS': 0,
            'Likely oncogenic': 6,
            'Oncogenic': 10,
        })

        # loop through in order until the score no longer meets the threshold
        classification = 'Benign'
        for c, score in class_list.items():
            if score_counter >= score:
                classification = c

        # for colouring the classification display
        class_css_list = {
            'Benign': 'info',
            'Likely benign': 'info',
            'VUS': 'warning',
            'Likely oncogenic': 'danger',
            'Oncogenic': 'danger',
        }
        css_class = class_css_list[classification]

        # save results to db
        codes = self.get_codes()
        for c in codes:
            #TODO might need to only save if model updates if hit on db is too high
            c.pending = selections_dict[c.code]['pending']
            c.applied = selections_dict[c.code]['applied']
            c.applied_strength = selections_dict[c.code]['strength']
            c.save()

        return score_counter, classification, css_class

    def codes_to_dict(self):
        """
        This might not be needed/ will need changing
        """
        # TODO get all codes in format on views page
        # hard coded list of combined codes
        # make combined entry and remove the respective single ones
        codes = self.get_codes()
        all_dict = {}

        pretty_print_dict = {
            'SA': 'Stand-alone',
            'VS': 'Very strong',
            'ST': 'Strong',
            'MO': 'Moderate',
            'SU': 'Supporting',
            'PE': 'Pending',
            'NA': 'Not applied',
        }

        for c in codes:
            if c.pending:
                css_class = 'warning'
                strength = 'PE'
            elif c.applied:
                if c.code_type() == 'Benign':
                    css_class = 'info'
                elif c.code_type() == 'Oncogenic':
                    css_class = 'danger'
                strength = c.applied_strength
            else:
                css_class = 'secondary'
                strength = 'NA'
            all_dict[c.code] = {
                'code': f'code_{c.code.lower()}',
                'value': f'{c.code}_{strength}',
                'applied': c.applied,
                'css_class': css_class,
                'pretty_print': f'{c.code} {pretty_print_dict[strength]}',
            }


        combinations = ['O3_B4']
        for c in combinations:
            code1, code2 = c.split('_')

            if (code1 in all_dict.keys()) and (code2 in all_dict.keys()):

                temp_dict = {
                    'code': f'code_{c.lower()}',
                }
                if all_dict[code1]['applied']:
                    temp_dict['value'] = f'{all_dict[code1]["value"]}|{all_dict[code2]["value"]}'
                    temp_dict['css_class'] = all_dict[code1]['css_class']
                    temp_dict['pretty_print'] = all_dict[code1]["pretty_print"]

                elif all_dict[code2]['applied']:
                    temp_dict['value'] = f'{all_dict[code1]["value"]}|{all_dict[code2]["value"]}'
                    temp_dict['css_class'] = all_dict[code2]['css_class']
                    temp_dict['pretty_print'] = all_dict[code2]["pretty_print"]

                else:
                    temp_dict['value'] = f'{all_dict[code1]["value"]}|{all_dict[code2]["value"]}'
                    temp_dict['pretty_print'] = all_dict[code1]['pretty_print']
                    if 'PE' in all_dict[code1]["value"]:
                        temp_dict['css_class'] = 'warning'
                    elif 'NA' in all_dict[code1]["value"]:
                        temp_dict['css_class'] = 'secondary'

                del all_dict[code1]
                del all_dict[code2]
                all_dict[c] = temp_dict

        return all_dict

    def codes_by_category(self):
        """ ordered list of codes for displaying template """
        pretty_print_dict = {
            'SA': 'Stand-alone',
            'VS': 'Very strong',
            'ST': 'Strong',
            'MO': 'Moderate',
            'SU': 'Supporting',
            'PE': 'Pending',
            'NA': 'Not applied',
        }

        config_file = os.path.join(BASE_DIR, f'app_svig/config/svig_{SVIG_CODE_VERSION}.yaml')
        with open(config_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        code_info = config["codes"]
        order_info = config["order"]

        code_objects = self.get_codes()

        all_check_objects = self.classification.get_all_checks()

        svig_codes = {}
        for code, values in order_info.items():
            svig_codes[code] = {
                'slug': slugify(code),
                "codes": {},
                "applied_codes": [],
                "complete": True,
                }
            for v in values:
                code_list = v.split("_")
                # list of dictionaries with description etc
                code_details = []
                for c in code_list:
                    code_details.append({c: code_info[c]})

                    # get applied codes
                    code_object = code_objects.get(code=c)
                    if code_object.applied:
                        svig_codes[code]["applied_codes"].append(f"{c}_{code_object.applied_strength}")
                    if code_object.pending:
                        svig_codes[code]["complete"] = False

                # dropdown options # TODO add +/- points to dropdown
                dropdown_options = [
                    {
                        "value": "|".join([f"{c}_PE" for c in code_list]),
                        "text": "Pending"
                    },
                    {
                        "value": "|".join([f"{c}_NA" for c in code_list]),
                        "text": "Not applied"
                    },
                ]
                all_checks = []
                if len(code_list) == 1:
                    for option in code_info[code_list[0]]["options"]:
                        dropdown_options.append({
                            "value": f"{code_list[0]}_{option}",
                            "text": f"{code_list[0]} {pretty_print_dict[option]}",
                        })

                    # all checks
                    for c in all_check_objects:
                        all_checks.append(c.get_codes(code_list[0]).display())

                else:
                    code_1, code_2 = code_list
                    for option in code_info[code_1]["options"]:
                        dropdown_options.append({
                            "value": f"{code_1}_{option}|{code_2}_NA",
                            "text": f"{code_1} {pretty_print_dict[option]}",
                        })
                    for option in code_info[code_2]["options"]:
                        dropdown_options.append({
                            "value": f"{code_1}_NA|{code_2}_{option}",
                            "text": f"{code_2} {pretty_print_dict[option]}",
                        })
                    # all checks
                    for c in all_check_objects:
                        code_1_display = c.get_codes(code_1).display()
                        code_2_display = c.get_codes(code_2).display()

                        if code_1_display == code_2_display:
                            all_checks.append(code_1_display)
                        else:
                            if code_1_display == "Not applied":
                                all_checks.append(code_2_display)
                            elif code_2_display == "Not applied":
                                all_checks.append(code_1_display)


                # add all to final dict
                svig_codes[code]["codes"][v] = {
                    'list': code_list,
                    'details': code_details,
                    'dropdown': dropdown_options,
                    'all_checks': all_checks,
                }

        return svig_codes

    def signoff_check(self, next_step):
        self.check_complete = True
        self.signoff_time = timezone.now()
        self.save()

        if next_step == 'E':
             self.classification.make_new_check()
        # TODO save results to classification obj if final check


class CodeAnswer(models.Model):
    """
    A check of an individual code

    """
    code = models.CharField(max_length=20)
    check_object = models.ForeignKey('Check', on_delete=models.CASCADE)
    pending = models.BooleanField(default=True)
    applied = models.BooleanField(default=False)
    applied_strength = models.CharField(max_length=20, blank=True, null=True)

    def code_type(self):
        if self.code[0] == 'B':
            return 'Benign'
        elif self.code[0] == 'O':
            return 'Oncogenic'

    def display(self):
        pretty_print_dict = {
            'SA': 'Stand-alone',
            'VS': 'Very strong',
            'ST': 'Strong',
            'MO': 'Moderate',
            'SU': 'Supporting',
            'PE': 'Pending',
            'NA': 'Not applied',
        }
        if self.pending:
            return "Pending"
        elif self.applied:
            return f"{self.code} {pretty_print_dict[self.applied_strength]}"
        else:
            return "Not applied"


class CanonicalList(models.Model):
    gene = models.CharField(max_length=20, null=True, blank=True)
    tumour_type = models.CharField(max_length=20, null=True, blank=True)
    hgvs_c = models.CharField(max_length=50, null=True, blank=True)
    hgvs_p = models.CharField(max_length=50, null=True, blank=True)
    variants = models.ManyToManyField('Variant', blank=True, related_name='canonical_list')  # TODO this is actually more like a variant instance, should be specific variant

    def contains_variant(self, variant):
        return self.objects.filter(variants__id=variant)
