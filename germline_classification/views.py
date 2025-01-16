from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def test(request):
    """
    temp
    """
    return render(request, 'germline_classification/test.html')