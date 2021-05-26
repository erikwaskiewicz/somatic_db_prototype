from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('worksheets', views.view_worksheets, name='view_worksheets'),
    path('worksheets/<str:worksheet_id>', views.view_samples, name='view_samples'),
    path('analysis/<str:dna_or_rna>/<str:sample_id>', views.analysis_sheet, name='analysis_sheet'),
]
