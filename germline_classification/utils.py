from django.db import transaction

from .models import *
from swgs.models import GermlineVariantInstance

@transaction.atomic
def create_classifications_from_swgs(list_of_variant_ids):
    """
    For a given SWGS patient analysis, create germline classification objects for all variants
    For SWGS, filtering is done in the app so we only want to pull displayed variants over to the classification module
    """
    for id in list_of_variant_ids:
        # get the SWGS germline variant instance
        germline_variant_instance_obj = GermlineVariantInstance.objects.get(id=id)
        # create a new classification object
        classification_obj = Classification.objects.create()
        # create a new SWGS variant classification
        swgs_variant_classification_obj = SWGSVariantClassification.objects.create(variant_instance=germline_variant_instance_obj, classification=classification_obj)
        swgs_variant_classification_obj.save()
    
def get_pending_classifications():
    """
    
    """
    all_pending_classifications = VariantClassification.objects.filter(
        classification__complete = False
    )
    print(all_pending_classifications)