from django.contrib.auth import views as auth_view
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_swgs, name="home_swgs"),
    path('view_runs/', views.view_runs, name="view_runs"),
    path('view_patient_analysis/', views.view_patient_analysis, name="view_patient_analysis")
]