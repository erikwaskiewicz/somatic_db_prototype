from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import *


# Create your views here.
@login_required
def view_classifications(request):
    """
    """
    all_classifications = Classification.objects.all()

    return render(request, 'app_svig/all_classifications.html', {'classifications': all_classifications})


@login_required
def classify(request, classification):
    return render(request, 'app_svig/svig_base.html', {'classification': classification})