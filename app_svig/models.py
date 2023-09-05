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

    def make_new_classification(self):
        """
        make a set of code answers
        TODO possily move to check obj as that might already be made?
        """
        # load in list of S-VIG codes from yaml
        config_file = os.path.join(BASE_DIR, f'app_svig/config/svig_{SVIG_CODE_VERSION}.yaml')
        with open(config_file) as f:
            svig_codes = yaml.load(f, Loader=yaml.FullLoader)

        # make 1st check object
        check_obj = Check.objects.create(
            classification = self
        )

        # loop through the codes and make code answer objects
        for code in svig_codes:
            CodeAnswer.objects.create(
                code = code,
                check_object = check_obj
            )


class Check(models.Model):
    """
    A check of a classification
    """
    classification = models.ForeignKey('Classification', on_delete=models.CASCADE)

    def classify(self):
        print('classify')
        # TODO collect all code answers and classify

    def get_codes(self):
        codes = CodeAnswer.objects.filter(check_object=self)
        return codes


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

            if v == 'NA':
                applied = False
                strength = None
            else:
                applied = True
                strength = v
                if code_type == 'B':
                    score_counter -= score_dict[strength]
                elif code_type == 'O':
                    score_counter += score_dict[strength]
            selections_dict[c] = {
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
            c.applied = selections_dict[c.code]['applied']
            c.applied_strength = selections_dict[c.code]['strength']
            c.save()

        return score_counter, classification, css_class


class CodeAnswer(models.Model):
    """
    A check of an individual code

    """
    code = models.CharField(max_length=20)
    check_object = models.ForeignKey('Check', on_delete=models.CASCADE)
    applied = models.BooleanField(default=False)
    applied_strength = models.CharField(max_length=20, blank=True, null=True)


#class Annotation(models.Model):
