from django.contrib.auth import views as auth_view
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_swgs, name="home_swgs")
]