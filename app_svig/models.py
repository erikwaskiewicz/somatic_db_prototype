from django.db import models

# Create your models here.
class Classification(models.Model):
    """
    An individual classification of a single variant

    """
    variant = models.ForeignKey('analysis.VariantPanelAnalysis', on_delete=models.CASCADE)
    full_classification = models.BooleanField(default = False)
    #svig_version = models.CharField()


    def __str__(self):
        return self.variant.variant_instance.hgvs_c

    def make_new_classification(self):
        # TODO make a set of code answers here
        print('hi')

'''
class Check(models.Model):
    """
    A check of a classification
    """
    classification = models.ForeignKey('CodeAnswer', on_delete=models.CASCADE)

    def classify(self):
        print('classify')
        # TODO collect all code answers and classify


#class CodeAnswer(models.Model):
    """
    A check of an individual code

    """
    code = models.CharField()
    check = models.ForeignKey('Check', on_delete=models.CASCADE)


#class Annotation(models.Model):
'''