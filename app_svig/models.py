from django.db import models
from somatic_variant_db.settings import BASE_DIR, SVIG_CODE_VERSION

import yaml
import os
from collections import OrderedDict


# Create your models here.
class Classification(models.Model):
    """
    An individual classification of a single variant

    """
    variant = models.ForeignKey('analysis.VariantPanelAnalysis', on_delete=models.CASCADE)
    full_classification = models.BooleanField(default=False)
    svig_version = models.CharField(max_length=20)

    def __str__(self):
        return self.variant.variant_instance.hgvs_c


class Check(models.Model):
    """
    A check of a classification
    """
    classification = models.ForeignKey('Classification', on_delete=models.CASCADE)

    def make_new_codes(self):
        """
        make a set of code answers against the current check
        """
        # load in list of S-VIG codes from yaml
        config_file = os.path.join(BASE_DIR, f'app_svig/config/svig_{SVIG_CODE_VERSION}.yaml')
        with open(config_file) as f:
            svig_codes = yaml.load(f, Loader=yaml.FullLoader)

        # loop through the codes and make code answer objects
        for code in svig_codes:
            CodeAnswer.objects.create(
                code = code,
                check_object = self
            )


    def get_codes(self):
        """
        Get all classification codes for the current check
        """
        codes = CodeAnswer.objects.filter(check_object=self)
        return codes


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
            }


        combinations = ['O3_B4']
        for c in combinations:
            code1, code2 = c.split('_')

            temp_dict = {
                'code': f'code_{c.lower()}',
            }
            if all_dict[code1]['applied']:
                temp_dict['value'] = f'{all_dict[code1]["value"]}|{all_dict[code2]["value"]}'
                temp_dict['css_class'] = all_dict[code1]['css_class']

            elif all_dict[code2]['applied']:
                temp_dict['value'] = f'{all_dict[code1]["value"]}|{all_dict[code2]["value"]}'
                temp_dict['css_class'] = all_dict[code2]['css_class']

            else:
                temp_dict['value'] = f'{all_dict[code1]["value"]}|{all_dict[code2]["value"]}'
                if 'PE' in all_dict[code1]["value"]:
                    temp_dict['css_class'] = 'warning'
                elif 'NA' in all_dict[code1]["value"]:
                    temp_dict['css_class'] = 'secondary'

            del all_dict[code1]
            del all_dict[code2]
            all_dict[c] = temp_dict

        return all_dict


    def codes_by_category(self):
        results_dict = {}

        # get applied codes
        applied_codes = self.get_codes()

        # load in list of S-VIG codes from yaml
        config_file = os.path.join(BASE_DIR, f'app_svig/config/svig_{SVIG_CODE_VERSION}.yaml')
        with open(config_file) as f:
            svig_codes = yaml.load(f, Loader=yaml.FullLoader)

        for code, values in svig_codes.items():
            # add category to the list if it isnt there already
            current_category = values['category']
            if current_category not in results_dict.keys():
                results_dict[current_category] = {
                    'applied_codes': [],
                    'complete': True
                }
                #TODO complete variable is hard coded at the mo, need to add pending option first

            # check if the code is applied and add to list if it is
            current_code = applied_codes.get(code=code)
            if values['type'] == 'benign':
                css_class = 'info'
            elif values['type'] == 'oncogenic':
                css_class = 'danger'
            if current_code.pending:
                results_dict[current_category]['complete'] = False
            if current_code.applied:
                temp_dict = {
                    'code': f'{current_code.code}_{current_code.applied_strength}',
                    'css_class': css_class,
                }
                
                results_dict[current_category]['applied_codes'].append(temp_dict)

        return results_dict


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

#class Annotation(models.Model):
