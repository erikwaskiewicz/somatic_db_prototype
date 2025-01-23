from django.urls import path

from . import views

app_name = "germline_classification"

urlpatterns = [
    path('', views.home, name='home'),
    path('pending_classifications', views.pending_classifications, name='pending_classifications'),
    path('completed_classifications', views.completed_classifications, name='completed_classifications'),
    path('classify_variant', views.classify_variant, name='classify_variant')
]