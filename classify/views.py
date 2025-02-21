from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *

from analysis.models import VariantPanelAnalysis

import json


# Create your views here.
@login_required
def view_classifications(request):
    """ """
    new_classifications_form = NewClassification()

    context = {
        "classifications": ClassifyVariantInstance.objects.all(),
        "new_form": new_classifications_form,
    }

    # when buttons are pressed
    if request.method == "POST":

        # only one button at the mo
        new_classifications_form = NewClassification(request.POST)
        if new_classifications_form.is_valid():
            # get variant instance
            var_inst = VariantPanelAnalysis(id=1)  # TODO this is hardcoded for testing
            var, _ = ClassifyVariant.objects.get_or_create(
                hgvs_c = "c.123A>T",
                hgvs_p = "p.Arg123His",
                genomic_coords = "7:12345A>T",
                genome_build = 38,
            )
            guideline_obj = Guideline.objects.get(pk=2) #TODO hardcoded for testing
            new_var_obj = AnalysisVariantInstance(
                variant=var,
                variant_instance=var_inst,
                guideline=guideline_obj
            )
            new_var_obj.save()
            new_var_obj.make_new_check()

            context["classifications"] = ClassifyVariantInstance.objects.all()

    return render(request, "classify/all_classifications.html", context)


@login_required
def classify(request, classification):
    """
    Page to perform classifications
    """
    # load in classification and check objects from url args
    classification_obj = ClassifyVariantInstance.objects.get(id=classification)
    current_check_obj = classification_obj.get_latest_check()

    # assign user
    if classification_obj.get_status() != "Complete":
        if current_check_obj.user == None:
            current_check_obj.user = request.user
            current_check_obj.save()

        if current_check_obj.user != request.user:
            raise PermissionDenied()

    # load context from classification obj
    context = {
        "sample_info": classification_obj.get_sample_info(),
        "variant_info": classification_obj.variant.get_variant_info(),
        "classification_info": classification_obj.get_classification_info(),
        "previous_classifications": classification_obj.get_previous_classifications(),
    }
    # TODO need way of splitting previous classifications into on site and off site

    # load in forms and add to context
    previous_class_choices = classification_obj.get_previous_classification_choices()
    context["forms"] = {
        "check_info_form": CheckInfoForm(),
        "reopen_check_info_form": ReopenCheckInfoForm(),
        "previous_class_form": PreviousClassificationForm(previous_class_choices=previous_class_choices),
        "reopen_previous_class_form": ReopenPreviousClassificationsForm(),
        "complete_classification_form": CompleteClassificationForm(),
        "reopen_classification_form": ReopenClassificationForm(),
        "finalise_form": FinaliseCheckForm(),
    }
    # TODO comments modal
    # TODO when checks disagree
    # TODO papers model with pubmed api
    # TODO finish previous classifications page
    # TODO send back option should be available all the time

    # ------------------------------------------------------------------------
    # when buttons are pressed
    if request.method == "POST":

        # button to confirm sample/variant tab has been checked
        if "check_info_form" in request.POST:
            check_info_form = CheckInfoForm(request.POST)
            if check_info_form.is_valid():
                current_check_obj.complete_info_tab()
                return redirect("perform-classification", classification)

        # button to reset sample/patient info tab
        if "reset_info_check" in request.POST:
            reopen_check_info_form = ReopenCheckInfoForm(request.POST)
            if reopen_check_info_form.is_valid():
                current_check_obj.reopen_info_tab()
                return redirect("perform-classification", classification)

        # button to select to use a previous classification or start a new one
        if "use_previous_class" in request.POST:
            previous_class_form = PreviousClassificationForm(
                request.POST, previous_class_choices=previous_class_choices
            )
            if previous_class_form.is_valid():
                use_previous = previous_class_form.cleaned_data["use_previous_class"]
                if use_previous == "previous":
                    print(use_previous)
                    # TODO change setting in classification obj and save link to reused classification

                elif use_previous == "new":
                    # change setting in classification obj and load up codes linked to check
                    current_check_obj.complete_previous_class_tab()
                    return redirect("perform-classification", classification_obj.pk)

        # button to revert previous/new classification form
        if "reset_previous_class_check" in request.POST:
            reopen_previous_class_form = ReopenPreviousClassificationsForm(request.POST)
            if reopen_previous_class_form.is_valid():
                current_check_obj.reopen_previous_class_tab()
                return redirect("perform-classification", classification)

        # button to complete classification
        if "complete_classification" in request.POST:
            complete_classification_form = CompleteClassificationForm(request.POST)
            if complete_classification_form.is_valid():
                final_score, final_class = (
                    current_check_obj.update_classification()
                )
                override = complete_classification_form.cleaned_data["override"]
                # TODO pathogenic not here, needs simplifing too
                if override == "No":
                    class_dict = {
                        "Benign": "B",
                        "Likely benign": "LB",
                        "VUS": "V",
                        "Likely oncogenic": "LO",
                        "Oncogenic": "O",
                    }
                    current_check_obj.final_class = class_dict[final_class]
                else:
                    current_check_obj.final_class = override
                current_check_obj.classification_check = True
                current_check_obj.final_score = final_score
                current_check_obj.save()
                return redirect("perform-classification", classification)

        # button to reopen classification
        if "reset_classification_check" in request.POST:
            reopen_classification_form = ReopenClassificationForm(request.POST)
            if reopen_classification_form.is_valid():
                current_check_obj.reopen_classification_tab()
                return redirect("perform-classification", classification)

        # button to finish check
        if "finalise_check" in request.POST:
            finalise_form = FinaliseCheckForm(request.POST)
            if finalise_form.is_valid():
                next_step = finalise_form.cleaned_data["next_step"]
                updated, err = classification_obj.signoff_check(
                    current_check_obj, next_step
                )
                if updated:
                    return redirect("view-all-classifications")
                else:
                    context["warning"] = [err]

    return render(request, "classify/classify_base.html", context)


def ajax_classify(request):
    """
    Generates new chunks of HTML for the classification summary boxes on the classify tab (within a div called class-box).
    Called in JS at bottom of classify_classify.html
    """
    if request.is_ajax():
        # get variables from AJAX input
        selections = json.loads(request.POST.get("selections"))
        check_pk = request.POST.get("check_pk")

        # load variables needed for new display
        current_check_obj = Check.objects.get(id=check_pk)
        current_check_obj.update_codes(selections)
        score, final_class = current_check_obj.update_classification()
        codes_by_category = current_check_obj.classification.get_codes_by_category()

        # empty dict for new html
        data = {}

        # make new classification box and add to results dict
        class_box_context = {
            "current_score": score,
            "current_class": final_class,
        }
        class_box_html = render_to_string(
            "classify/ajax/classification.html", class_box_context
        )
        data["class_box"] = class_box_html

        # make the code summary and complete true/false segments for each category of code and add to results dict
        for category, value in codes_by_category.items():

            # summary of codes applied
            html = render_to_string(
                "classify/ajax/category_summary.html",
                {"applied_codes": value["applied_codes"]},
            )
            data[f'codes_summary_{value["slug"].replace("-", "_")}'] = html

            # complete yes/no
            html = render_to_string(
                "classify/ajax/category_complete.html", {"complete": value["complete"]}
            )
            data[f'complete_{value["slug"].replace("-", "_")}'] = html

        return JsonResponse(data)
