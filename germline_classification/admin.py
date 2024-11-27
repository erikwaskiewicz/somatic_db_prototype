from django.contrib import admin

from .models import *

"""
Add Germline classification models to the Django admin page
Fields that can be searched by are defined in the search_fields variable
Fields displayed on the admin page are defined in the list_display variable
"""

class ClassificationCriteriaStrengthAdmin(admin.ModelAdmin):
    list_display = ["strength", "evidence_points"]
    search_fields = ["strength", "evidence_points"]

admin.site.register(ClassificationCriteriaStrength, ClassificationCriteriaStrengthAdmin)

class ClassificationCriteriaCodeAdmin(admin.ModelAdmin):
    list_display = ["code", "pathogenic_or_benign", "description"]
    search_fields = ["code", "pathogenic_or_benign", "description"]

admin.site.register(ClassificationCriteriaCode, ClassificationCriteriaCodeAdmin)

class ClassificationCriteriaAdmin(admin.ModelAdmin):
    list_display = ["strength", "code"]
    search_fields = ["strength__strength", "code__code"]

admin.site.register(ClassificationCriteria, ClassificationCriteriaAdmin)

class ClassificationAdmin(admin.ModelAdmin):
    filter_horizontal = ["criteria_applied"]

admin.site.register(Classification, ClassificationAdmin)