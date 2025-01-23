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
    list_display = ["get_code", "get_strength"]
    search_fields = ["code__code", "strength__strength"]

    def get_strength(self, obj):
        return f"{obj.strength.strength}:{str(obj.strength.evidence_points)}"
    get_strength.short_description = "Strength"
    get_strength.admin_order_field = "strength__strength"
    
    def get_code(self, obj):
        return obj.code.code
    get_code.short_description = "Code"
    get_code.admin_order_field = "code__code"

admin.site.register(ClassificationCriteria, ClassificationCriteriaAdmin)

class ClassificationAdmin(admin.ModelAdmin):
    filter_horizontal = ["criteria_applied"]

admin.site.register(Classification, ClassificationAdmin)

class AnalysisVariantClassificationAdmin(admin.ModelAdmin):
    list_display = ["variant_instance", "classification"]

admin.site.register(AnalysisVariantClassification, AnalysisVariantClassificationAdmin)

class SWGSVariantClassificationAdmin(admin.ModelAdmin):
    list_display = ["variant_instance", "classification"]

admin.site.register(SWGSVariantClassification, SWGSVariantClassificationAdmin)

#TODO update add other models