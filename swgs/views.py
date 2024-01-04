from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home_swgs(request):
    """
    """
    return render(request, 'swgs/home.html', {})