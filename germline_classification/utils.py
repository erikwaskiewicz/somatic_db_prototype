from django.db import transaction
from django.db.models import Q

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
            sample = classification.variant_instance.patient_analysis.germline_sample.sample_id
            worksheet = classification.variant_instance.patient_analysis.run.worksheet
            variant = classification.variant_instance.variant.variant
            hgvsc, hgvsp, gene = classification.variant_instance.get_default_hgvs_nomenclature()
            classification_info_dict["sample"] = sample
            classification_info_dict["worksheet"] = worksheet
            classification_info_dict["genomic_coordinate"] = variant
            classification_info_dict["hgvsc"], classification_info_dict["hgvsp"], classification_info_dict["gene"] = hgvsc, hgvsp, gene

        previous_classifications = get_all_classifications_for_a_variant(variant)
        classification_info_dict["previous_classifications"] = previous_classifications
        print(classification_info_dict)
        all_classifications.append(classification_info_dict)

    return all_classifications

def get_all_classifications_for_a_variant(variant):
    """
    For a given variant (format 'chr1:12345:A>T') find all classifications accross all assays
    """
    # Query over all assays to find the variants queried
    variant_classifications = VariantClassification.objects.filter(
        (
            (Q(analysisvariantclassification__variant_instance__variant_instance__variant__variant=variant) & Q(analysisvariantclassification__classification__complete=True)) |
            (Q(swgsvariantclassification__variant_instance__variant__variant=variant) & Q(swgsvariantclassification__classification__complete=True))
        )
    )

    previous_classifications = []

    for c in variant_classifications:
        user = c.classification.user
        signoff_time = c.classification.signoff_time
        final_classification, total_score =  c.classification.perform_classification()
        print(c.variant_instance)
        print(c.classification)
        classification_dict = {
            "user": user,
            "signoff_time": signoff_time.strftime("%d/%m/%Y"),
            "final_classification": final_classification,
            "total_score": total_score
        }
        print(classification_dict)
        previous_classifications.append(classification_dict)

    print(previous_classifications)

    return previous_classifications
