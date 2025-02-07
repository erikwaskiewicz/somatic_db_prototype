from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from .models import *


class VariantAdmin(admin.ModelAdmin):
    search_fields = ["svd_variant"]


class ClassificationAdmin(admin.ModelAdmin):
    search_fields = ["variant"]


class CheckAdmin(admin.ModelAdmin):
    search_fields = ["classification"]


class CodeAnswerAdmin(admin.ModelAdmin):
    search_fields = ["code", "check_object"]


admin.site.register(Variant, VariantAdmin)
admin.site.register(Classification, ClassificationAdmin)
admin.site.register(Check, CheckAdmin)
admin.site.register(CodeAnswer, CodeAnswerAdmin)

# UPDATED ADMIN PANEL FOR CLASSIFY please change as needed

@admin.register(Guideline)
class GuidelineAdmin(admin.ModelAdmin):
    search_fields = ["guideline"]
    filter_horizontal = ["criteria"]

@admin.register(ClassificationCriteriaStrength)
class ClassificationCriteriaStrengthAdmin(admin.ModelAdmin):
    search_fields = ["strength"]
    list_display = ["strength", "evidence_points"]

@admin.register(ClassificationCriteriaCode)
class ClassificationCriteriaCodeAdmin(admin.ModelAdmin):
    search_fields = ["code"]
    list_display = ["code", "pathogenic_or_benign", "category"]

@admin.register(ClassificationCriteria)
class ClassificationCriteriaAdmin(admin.ModelAdmin):
    search_fields = ["code", "strength"]

@admin.register(ClassifyVariant)
class ClassifyVariantAdmin(admin.ModelAdmin):
    search_fields = ["hgvsc", "hgvsp", "b38_coords", "b37_coords"]

class ClassifyVariantInstanceChildAdmin(PolymorphicChildModelAdmin):
    base_model = ClassifyVariantInstance

@admin.register(ClassifyVariantInstance)
class ClassifyVariantInstanceAdmin(PolymorphicParentModelAdmin):
    base_model = ClassifyVariantInstance
    child_models = (AnalysisVariantInstance, SWGSGermlineVariantInstance, SWGSSomaticVaraintInstance, ManualVariantInstance)
    list_filter = (PolymorphicChildModelFilter,)

@admin.register(AnalysisVariantInstance)
class AnalysisVariantInstanceAdmin(ClassifyVariantInstanceChildAdmin):
    base_model = AnalysisVariantInstance

@admin.register(SWGSGermlineVariantInstance)
class SWGSGermlineVariantInstanceAdmin(ClassifyVariantInstanceChildAdmin):
    base_model = SWGSGermlineVariantInstance

@admin.register(SWGSSomaticVaraintInstance)
class SWGSSomaticVariantInstanceAdmin(ClassifyVariantInstanceChildAdmin):
    base_model = SWGSSomaticVaraintInstance

@admin.register(ManualVariantInstance)
class ManualVariantInstanceAdmin(ClassifyVariantInstanceChildAdmin):
    base_model = ManualVariantInstance