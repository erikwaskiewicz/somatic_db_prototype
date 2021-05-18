from django.urls import path
from . import views

urlpatterns = [
    path('', views.analysis_sheet, name='analysis_sheet'),
]
