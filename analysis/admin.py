from django.contrib import admin
from .models import *


admin.site.register(Run)
admin.site.register(Worksheet)

class SampleAdmin(admin.ModelAdmin):
    list_display = ('sample_id', 'sample_name', 'sample_type')
admin.site.register(Sample, SampleAdmin)


class PanelAdmin(admin.ModelAdmin):
    list_display = ('panel_name', 'dna_or_rna')
admin.site.register(Panel, PanelAdmin)

class SampleAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'worksheet', 'sample', 'panel')
admin.site.register(SampleAnalysis, SampleAnalysisAdmin)

class CheckAdmin(admin.ModelAdmin):
    list_display = ('id', 'analysis', 'status', 'user')
admin.site.register(Check, CheckAdmin)

class VariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'genomic_37', 'genomic_38')
admin.site.register(Variant, VariantAdmin)


class VariantInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'sample', 'variant')
admin.site.register(VariantInstance, VariantInstanceAdmin)

class VariantPanelAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'sample_analysis', 'variant_instance')
admin.site.register(VariantPanelAnalysis, VariantPanelAnalysisAdmin)

class VariantListAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'list_type' )
admin.site.register(VariantList, VariantListAdmin )


class VariantToVariantListAdmin(admin.ModelAdmin):
    list_display = ( 'variant_list', 'variant', 'classification')
admin.site.register(VariantToVariantList, VariantToVariantListAdmin)


class VariantCheckAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'variant_analysis', 'check_object', 'decision')
admin.site.register(VariantCheck, VariantCheckAdmin)

admin.site.register(Gene)


admin.site.register(GeneCoverageAnalysis)
admin.site.register(RegionCoverageAnalysis)
admin.site.register(GapsAnalysis)
admin.site.register(Fusion)
admin.site.register(FusionAnalysis)
admin.site.register(FusionCheck)
admin.site.register(FusionPanelAnalysis)


