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

class GeneCoverageAnalysisAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'sample', 'gene' )
admin.site.register(GeneCoverageAnalysis, GeneCoverageAnalysisAdmin )

class RegionCoverageAnalysisAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'gene', 'hgvs_c' )
admin.site.register(RegionCoverageAnalysis, RegionCoverageAnalysisAdmin)


class GapAnalysisAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'gene', 'hgvs_c' )
admin.site.register(GapsAnalysis, GapAnalysisAdmin)


class FusionAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'fusion_genes' )
admin.site.register(Fusion, FusionAdmin )


class FusionAnalysisAdmin(admin.ModelAdmin):
    list_display = ( 'sample', 'fusion_genes' )
admin.site.register(FusionAnalysis, FusionAnalysisAdmin)


class FusionCheckAdmin(admin.ModelAdmin):
    list_display = ( 'fusion_analysis', 'check_object' , 'decision')
admin.site.register(FusionCheck, FusionCheckAdmin)

class FusionPanelAnalysisAdmin(admin.ModelAdmin):
    list_display = ( 'sample_analysis', 'fusion_instance' )
admin.site.register(FusionPanelAnalysis, FusionPanelAnalysisAdmin)


