from django.db import models

# Create your models here.
class Classification(models.Model):
    """
    An individual classification of a single variant

    """
    variant = models.ForeignKey('analysis.VariantPanelAnalysis', on_delete=models.CASCADE)


    def __str__(self):
        return self.variant.variant_instance.hgvs_c
