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
    
def get_classifications(pending_or_completed):
    """
    Get all pending or completed classifications over WGS and analysis apps
    """
    all_classifications = []

    if pending_or_completed == "pending":
        classification_complete = False
    else:
        classification_complete = True

    all_pending_classifications_query = VariantClassification.objects.filter(
        classification__complete = classification_complete
    )

    # for each classification, create a dictionary of all the required information
    for classification in all_pending_classifications_query:

        classification_info_dict = {
            "id": classification.id,
            "origin": "",
            "sample": "",
            "worksheet": "",
            "genomic_coordinate": "",
            "hgvsc": "",
            "hgvsp": "",
            "gene": ""
        }

        if classification.origin == "WGS":
            classification_info_dict["origin"] = "WGS"
            classification_info_dict["sample"] = classification.variant_instance.patient_analysis.germline_sample.sample_id
            classification_info_dict["worksheet"] = classification.variant_instance.patient_analysis.run.worksheet
            classification_info_dict["genomic_coordinate"] = classification.variant_instance.variant.variant
            classification_info_dict["hgvsc"], classification_info_dict["hgvsp"], classification_info_dict["gene"] = classification.variant_instance.get_default_hgvs_nomenclature()

        if classification_complete:
            outcome, score =  classification.classification.perform_classification()
            classification_info_dict["outcome"] = outcome
            classification_info_dict["score"] = score

        all_classifications.append(classification_info_dict)

    print(all_classifications)
    return all_classifications