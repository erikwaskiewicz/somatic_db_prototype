from django.contrib import admin
from .models import *


class ClassificationAdmin(admin.ModelAdmin):
    search_fields = ['variant']

class CheckAdmin(admin.ModelAdmin):
    search_fields = ['classification']

class CodeAnswerAdmin(admin.ModelAdmin):
    search_fields = ['code', 'check_object']

admin.site.register(Classification, ClassificationAdmin)
admin.site.register(Check, CheckAdmin)
admin.site.register(CodeAnswer, CodeAnswerAdmin)
