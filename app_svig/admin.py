from django.contrib import admin
from .models import *


class ClassificationAdmin(admin.ModelAdmin):
    search_fields = ['variant']

admin.site.register(Classification, ClassificationAdmin)
