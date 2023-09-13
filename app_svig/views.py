from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from somatic_variant_db.settings import SVIG_CODE_VERSION

from app_svig.models import *
from app_svig.forms import *

from analysis.models import VariantPanelAnalysis

import json

# Create your views here.
@login_required
def view_classifications(request):
    """
    """
    new_classifications_form = NewClassification()

    context = {
        'classifications': Classification.objects.all(),
        'new_form': new_classifications_form,
    }

    # when buttons are pressed
    if request.method == 'POST':

        # only one button at the mo
        new_classifications_form = NewClassification(request.POST)
        if new_classifications_form.is_valid():
            # get variant instance
            var = VariantPanelAnalysis(id = 291)

            new_classification_obj = Classification(
                variant = var,
                svig_version = SVIG_CODE_VERSION,
            )
            new_classification_obj.save()
            new_check_obj = Check(
                classification = new_classification_obj,
            )
            new_check_obj.save()

            context['classifications'] = Classification.objects.all()


    return render(request, 'app_svig/all_classifications.html', context)


@login_required
def classify(request, classification):
    """
    Page to perform S-VIG classifications
    """
    # load in classification and check objects from url args
    classification_obj = Classification.objects.get(id = classification)
    check_obj = Check.objects.filter(classification = classification_obj)[0] #TODO this probably needs to be more robust for multiple checks/might be wrong

    # load in forms
    check_info_form = CheckInfoForm()
    previous_class_form = PreviousClassificationForm()
    reopen_previous_class_form = ResetPreviousClassificationsForm()

    # get sample specific variables
    sample_info = {
        'sample_id': classification_obj.variant.sample_analysis.sample.sample_id,
        'worksheet_id': classification_obj.variant.sample_analysis.worksheet.ws_id,
        'svd_panel': classification_obj.variant.sample_analysis.panel,
        'specific_tumour_type': 'TODO e.g. AML, add to sample analysis model? And set options from panel model?',
    }

    # get variant specific variables
    build = classification_obj.variant.variant_instance.variant.genome_build
    if build == 37:
        build_css_tag = 'info'
    elif build == 38:
        genome_build = 'success'

    variant_info = {
        'genomic': classification_obj.variant.variant_instance.variant.variant,
        'build': build,
        'build_css_tag': build_css_tag,
        'hgvs_c': classification_obj.variant.variant_instance.hgvs_c,
        'hgvs_p': classification_obj.variant.variant_instance.hgvs_p,
        'consequence': 'TODO',
        'mode_action': 'TODO',
    }

    # get variables for this classification
    classification_info = {
            'classification_obj': classification_obj,
            'current_check': check_obj,
    }

    # load into context
    context = {
        'sample_info': sample_info,
        'variant_info': variant_info,
        'classification_info': classification_info,
        'check_info_form': check_info_form,
        'previous_class_form': previous_class_form,
        'reopen_previous_class_form': reopen_previous_class_form,
    }

    # load in extra classifation variables if its a full classification
    if classification_obj.full_classification:
        current_score, current_class, class_css = check_obj.classify()

        context['all_codes'] = check_obj.codes_to_dict()
        context['codes_by_category'] = check_obj.codes_by_category()
        context['classification_info']['current_class'] = current_class
        context['classification_info']['current_score'] = current_score
        context['classification_info']['class_css'] = class_css


    # ------------------------------------------------------------------------
    # when buttons are pressed
    if request.method == 'POST':

        # button to confirm smaple/variant tab has been checked
        if 'check_info_form' in request.POST:
            check_info_form = CheckInfoForm(request.POST)
            if check_info_form.is_valid():
                print(check_info_form)
                # TODO update in models

        # button to select to use a previous classification or start a new one
        if 'use_previous_class' in request.POST:
            previous_class_form = PreviousClassificationForm(request.POST)
            if previous_class_form.is_valid():
                use_previous = previous_class_form.cleaned_data['use_previous_class']
                if use_previous == 'True':
                    print(use_previous)
                    #TODO change setting in classification obj and save link to reused classification

                elif use_previous == 'False':
                    # change setting in classification obj and load up codes linked to check
                    classification_obj.full_classification = True
                    classification_obj.save()
                    check_obj.make_new_codes()
                    # TODO - stop this from resubmitting on refresh

                    # reload context
                    current_score, current_class, class_css = check_obj.classify()
                    context['classification_info']['current_class'] = current_class
                    context['classification_info']['current_score'] = current_score
                    context['classification_info']['class_css'] = class_css


        # button to revert previous/new classification form
        if 'reset_previous' in request.POST:
            reopen_previous_class_form = ResetPreviousClassificationsForm(request.POST)
            if reopen_previous_class_form.is_valid():
                classification_obj.full_classification = False
                classification_obj.save()
                check_obj.remove_codes()

    return render(request, 'app_svig/svig_base.html', context)


def ajax_svig(request):
    """
    Generates new chunks of HTML for the classification summary boxes on the S-VIG tab (within a div called class-box). 
    Called in JS at bottom of svig_classify.html
    """
    if request.is_ajax():
        # get variables from AJAX input
        selections = json.loads(request.POST.get('selections'))
        check_pk = request.POST.get('check_pk')

        # load variables needed for new display
        check_obj = Check.objects.get(id=check_pk)
        score, final_class, css_class = check_obj.update_codes(selections)
        codes_by_category = check_obj.codes_by_category()

        # empty dict for new html
        data = {}

        # make new classification box and add to results dict
        class_box_context = {
            'current_score': score,
            'current_class': final_class,
            'class_css': css_class,
        }
        class_box_html = render_to_string('app_svig/ajax/classification.html', class_box_context)
        data['class_box'] = class_box_html

        # make the code summary and complete true/false segments for each category of code and add to results dict
        for category, value in codes_by_category.items():

            # summary of codes applied
            html = render_to_string('app_svig/ajax/category_summary.html', {'applied_codes': value['applied_codes']})
            data[f'codes_summary_{category}'] = html

            # complete yes/no
            html = render_to_string('app_svig/ajax/category_complete.html', {'complete': value['complete']})
            data[f'complete_{category}'] = html

        return JsonResponse(data)
