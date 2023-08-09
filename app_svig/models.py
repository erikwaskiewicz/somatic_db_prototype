from django.db import models
from somatic_variant_db.settings import BASE_DIR, SVIG_CODE_VERSION

import yaml
import os


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


class CodeAnswer(models.Model):
    """
    A check of an individual code

    """
    code = models.CharField(max_length=20)
    check_object = models.ForeignKey('Check', on_delete=models.CASCADE)
    applied = models.BooleanField(default=False)
    applied_strength = models.CharField(max_length=20, blank=True, null=True)


#class Annotation(models.Model):
