from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.view_classifications, name='view-all-svig'),
    path('classify/<str:classification>', views.classify, name='svig-analysis'),
    path('ajax/submit_svig_selections/', views.ajax_svig, name='ajax-svig'),
]
