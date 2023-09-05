from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *

# Create your views here.
@login_required
def view_classifications(request):
    """
    """
    all_classifications = Classification.objects.all()

    return render(request, 'app_svig/all_classifications.html', {'classifications': all_classifications})


@login_required
def classify(request, classification):
    classification_obj = Classification.objects.get(id = classification)
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

    context = {
        'classification': classification_obj,
        'previous_class_form': previous_class_form,
        'reopen_previous_class_form': reopen_previous_class_form,
        'sample_info': sample_info,
        'variant_info': variant_info,
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

    return render(request, 'app_svig/svig_base.html', context)
