import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import *
from .utils import *

@login_required
def home(request):
    return render(request, 'germline_classification/home.html')

@login_required
def pending_classifications(request):
    """
    Get and display all pending variant classifications
    """

    all_pending_classifications  = get_classifications("pending")

    context = {
        "classifications": all_pending_classifications
    }

    return render(request, "germline_classification/pending_classifications.html", context)

@login_required
def completed_classifications(request):
    """
    Get and display all pending variant classifications
    """

    all_pending_classifications  = get_classifications("completed")

    context = {
        "classifications": all_pending_classifications
    }

    return render(request, "germline_classification/completed_classifications.html", context)


@login_required
def classify_variant(request, variant_classification_id):
    """
    Classify a single variant
    """
    #TODO ADD ID IN TO THIS

    # set up forms 
    classify_form = ClassifyForm()
    warnings = []
    final_classification = ""

    # get classification object
    variant_classification_obj = VariantClassification.objects.get(pk=variant_classification_id)
    classification_obj = variant_classification_obj.classification

    if request.method == 'POST':

        classify_form = ClassifyForm(request.POST)
        print(classify_form.is_valid())
        if classify_form.is_valid():

            # get user
            current_user = request.user

            # get time
            now = datetime.datetime.today()

            # get data from form
            population_codes = classify_form.cleaned_data["population_codes"]
            predictive_codes = classify_form.cleaned_data["predictive_codes"]
            functional_codes = classify_form.cleaned_data["functional_codes"]
            de_novo_codes = classify_form.cleaned_data["de_novo_codes"]
            segregation_codes = classify_form.cleaned_data["segregation_codes"]
            allelic_codes = classify_form.cleaned_data["allelic_codes"]
            phenotype_codes = classify_form.cleaned_data["phenotype_codes"]
            
            # get all the codes together
            all_codes = []
            for code_list in ([population_codes, predictive_codes, functional_codes, de_novo_codes, segregation_codes, allelic_codes, phenotype_codes]):
                if not isinstance(code_list, list):
                    code_list = [code_list]
                for code in code_list:
                    if code != "None":
                        all_codes.append(int(code))

            # create a new classification object
            # update information with user and time
            classification_obj.user = current_user
            classification_obj.signoff_time = now

            # add codes
            for code in all_codes:
                code_obj = ClassificationCriteria.objects.get(id=code)
                classification_obj.criteria_applied.add(code_obj)
            
            classification, score = classification_obj.perform_classification()
            final_classification = f"{classification} ({score})"
            #context["final_classification"] = final_classification

            # set classification as complete
            classification_obj.complete = True
            classification_obj.save()

            #return redirect('classify_variant')

    context = {
        "classify_form": classify_form,
        "warning": warnings,
        "final_classification": final_classification
    }

    return render(request, "germline_classification/classify_variant.html", context)