from django.contrib import admin
from .models import *


class AnnotationVersionsAdmin(admin.ModelAdmin):
    search_fields = ["version"]


class VariantAdmin(admin.ModelAdmin):
    search_fields = ["svd_variant"]


class ClassificationAdmin(admin.ModelAdmin):
    search_fields = ["variant"]


class CheckAdmin(admin.ModelAdmin):
    search_fields = ["classification"]


class CodeAnswerAdmin(admin.ModelAdmin):
    search_fields = ["code", "check_object"]


admin.site.register(AnnotationVersions, AnnotationVersionsAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(Classification, ClassificationAdmin)
admin.site.register(Check, CheckAdmin)
admin.site.register(CodeAnswer, CodeAnswerAdmin)
admin.site.register(CanonicalList)
