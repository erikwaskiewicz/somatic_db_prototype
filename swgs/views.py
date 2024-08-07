from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from swgs.models import *

@login_required
def home_swgs(request):
    """
    """
    return render(request, 'swgs/home.html', {})

@login_required
def view_runs(request):
    """
    View runs / worksheets
    """

    # get all the runs
    runs = Run.objects.all().order_by("-run")

    # context dictionary
    context = {
        'runs': runs
    }

    return render(request, "swgs/view_runs.html", context)

@login_required
def view_patient_analysis(request, patient_id):
    """
    View variants in a PatientAnalysis
    """
    