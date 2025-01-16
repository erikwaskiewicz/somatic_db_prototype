import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import *

@login_required
def classify_variant(request):
    """
    Classify a single variant
    """

    # set up forms 
    classify_form = ClassifyForm()
    warnings = []

    if request.method == 'POST':

        classify_form = ClassifyForm(request.POST)

        if classify_form.is_valid():

            # get user
            current_user = request.user

            # get time
            now = datetime.datetime.today()

            # get data from form

    context = {
        "classify_form": classify_form,
        "warning": warnings
    }

    return render(request, "germline_classification/classify_variant.html", context)