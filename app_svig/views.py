from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *

import json

# Create your views here.
@login_required
def view_classifications(request):
    """
    """
    all_classifications = Classification.objects.all()

    return render(request, 'app_svig/all_classifications.html', {'classifications': all_classifications})


@login_required
def classify(request, classification):
    """

    """
    classification_obj = Classification.objects.get(id = classification)
    check_obj = Check.objects.filter(classification = classification_obj)[0] #TODO this probably needs to be more robust for multiple checks/might be wrong
    previous_class_form = PreviousClassificationForm()
    reopen_previous_class_form = ResetPreviousClassificationsForm()

    sample_info = {
        'sample_id': classification_obj.variant.sample_analysis.sample.sample_id,
        'worksheet_id': classification_obj.variant.sample_analysis.worksheet.ws_id,
        'svd_panel': classification_obj.variant.sample_analysis.panel,
        'specific_tumour_type': 'TODO e.g. AML, add to sample analysis model? And set options from panel model?',
    }

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

    current_score, current_class, class_css = check_obj.classify()

    all_codes = check_obj.codes_to_dict()

    classification_info = {
        'classification_obj': classification_obj,
        'current_check': check_obj,
        'current_class': current_class,
        'current_score': current_score,
        'class_css': class_css,
    }

    context = {
        'sample_info': sample_info,
        'variant_info': variant_info,
        'classification_info': classification_info,
        'all_codes': all_codes,
        'previous_class_form': previous_class_form,
        'reopen_previous_class_form': reopen_previous_class_form,
    }

    # when buttons are pressed
    if request.method == 'POST':

        # button to select to use a previous classification or start a new one
        if 'use_previous_class' in request.POST:
            previous_class_form = PreviousClassificationForm(request.POST)
            if previous_class_form.is_valid():
                use_previous = previous_class_form.cleaned_data['use_previous_class']
                if use_previous == 'True':
                    print(use_previous)
                    #TODO change setting in classification obj and save link to reused classification

                elif use_previous == 'False':
                    print('no', use_previous)
                    # TODO change setting in classification obj and load up codes
                    classification_obj.full_classification = True
                    classification_obj.save()
                    classification_obj.make_new_classification()

                    # reload context
                    context['classification'] = classification_obj

        # button to revert previous/new classification form
        if 'reset_previous' in request.POST:
            reopen_previous_class_form = ResetPreviousClassificationsForm(request.POST)
            if reopen_previous_class_form.is_valid():
                print('reset')
                classification_obj.full_classification = False
                classification_obj.save()
                #TODO - remove svig codes for this check

    return render(request, 'app_svig/svig_base.html', context)


def ajax_svig(request):
    """
    Generates a new chunk of HTML for the classification summary box on the S-VIG tab (within a div called class-box)
    """
    if request.is_ajax():

        selections = json.loads(request.POST.get('selections'))
        check_pk = request.POST.get('check_pk')
        check_obj = Check.objects.get(id=check_pk)
        score, final_class, css_class = check_obj.update_codes(selections)


        #TODO - calculate final class and score and pass in context below, save answers to db
        context = {
            'current_score': score,
            'current_class': final_class,
            'class_css': css_class,
        }

        html = render_to_string('app_svig/ajax/classification.html', context)
        return HttpResponse(html)
