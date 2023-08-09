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

    context = {
        'classification': classification_obj,
        'previous_class_form': previous_class_form
    }

    # when buttons are pressed
    if request.method == 'POST':
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

    return render(request, 'app_svig/svig_base.html', context)
