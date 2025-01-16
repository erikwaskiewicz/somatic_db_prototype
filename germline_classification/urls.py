from django.urls import path

from . import views

urlpatterns = [
    path('classify_variant', views.classify_variant, name='classify_variant')
]