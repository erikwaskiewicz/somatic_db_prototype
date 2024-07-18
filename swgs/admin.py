from django.contrib import admin

from .models import *

"""
Add SWGS models to the Django admin page
Fields that can be searched by are defined in the search_fields variable
Fields displayed on the admin page are defined in the list_display variable
"""

class GeneAdmin(admin.ModelAdmin):
    list_display = ["gene"]
    search_fields = ["gene"]

admin.site.register(Gene, GeneAdmin)

class TranscriptAdmin(admin.ModelAdmin):
    list_display = ["transcript", "gene"]
    search_fields = ["transcript", "gene"]

admin.site.register(Transcript, TranscriptAdmin)

class PatientAdmin(admin.ModelAdmin):
    list_display = ["nhs_number"]
    search_fields = ["nhs_number"]

admin.site.register(Patient, PatientAdmin)

class SampleAdmin(admin.ModelAdmin):
    list_display = ["sample_id"]
    search_fields = ["sample_id"]

admin.site.register(Sample, SampleAdmin)

class IndicationAdmin(admin.ModelAdmin):
    list_display = ["indication", "indication_pretty_print"]
    search_fields = ["indication", "indication_pretty_print"]

    #TODO add panels, make sure we're returning something sensible
    """ example from analysis module
    # get panel name rather than panel ID
    def get_panel(self, obj):
        return obj.panel.panel_name
    get_panel.short_description = 'Panel'
    get_panel.admin_order_field = 'panel__panel_name'
    """

admin.site.register(Indication, IndicationAdmin)

class PanelAdmin(admin.ModelAdmin):
    list_display = ["panel_name", "panel_version", "panel_approved", "lims_code"]
    search_fields = ["panel_name", "lims_code"]

admin.site.register(Panel, PanelAdmin)

class RunAdmin (admin.ModelAdmin):
    list_display = ["run", "worklist"]
    search_fields = ["run", "worklist"]

admin.site.register(Run, RunAdmin)

class PatientAnalysisAdmin(admin.ModelAdmin):
    list_display = ["patient", "tumour_sample", "germline_sample", "indication", "run"]
    search_fields = ["patient", "tumour_sample", "germline_sample", "run"]

admin.site.register(PatientAnalysis, PatientAnalysisAdmin)

class QCSomaticVAFDistributionAdmin(admin.ModelAdmin):
    list_display = ["status", "low_vaf_proportion"]
    search_fields = ["status"]

admin.site.register(QCSomaticVAFDistribution, QCSomaticVAFDistributionAdmin)

class QCTumourInNormalContaminationAdmin(admin.ModelAdmin):
    list_display = ["status"]
    search_fields = ["status"]

admin.site.register(QCTumourInNormalContamination, QCTumourInNormalContaminationAdmin)

class QCGermlineCNVQualityAdmin(admin.ModelAdmin):
    list_display = ["status", "passing_cnv_count", "passing_fraction", "log_loss_gain"]
    search_fields = ["status"]

admin.site.register(QCGermlineCNVQuality, QCGermlineCNVQualityAdmin)

class QCNTCContaminationAdmin(admin.ModelAdmin):
    list_display = ["status", "ntc_contamination"]
    search_fields = ["status"]

admin.site.register(QCNTCContamination, QCNTCContaminationAdmin)

class GenomeBuildAdmin(admin.ModelAdmin):
    list_display = ["genome_build"]
    search_fields = ["genome_build"]

admin.site.register(GenomeBuild, GenomeBuildAdmin)

class VariantAdmin(admin.ModelAdmin):
    list_display = ["variant", "genome_build"]
    search_fields = ["variant"]

admin.site.register(Variant, VariantAdmin)

class GermlineVariantInstanceAdmin(admin.ModelAdmin):
    list_display = ["variant", "patient_analysis", "ad", "af"]
    search_fields = ["variant", "patient_analysis"]

admin.site.register(GermlineVariantInstance, GermlineVariantInstanceAdmin)

class SomaticVariantInstanceAdmin(admin.ModelAdmin):
    list_display = ["variant", "patient_analysis", "ad", "af"]
    search_fields = ["variant", "patient_analysis"]

admin.site.register(SomaticVariantInstance, SomaticVariantInstanceAdmin)

class VEPAnnotationsConsequenceAdmin(admin.ModelAdmin):
    list_display = ["consequence", "impact"]
    search_fields = ["consequence"]

admin.site.register(VEPAnnotationsConsequence, VEPAnnotationsConsequenceAdmin)

class VEPAnnotationsImpactAdmin(admin.ModelAdmin):
    list_display = ["impact"]
    search_fields = ["impact"]

admin.site.register(VEPAnnotationsImpact, VEPAnnotationsImpactAdmin)

class VEPAnnotationsExistingVariationAdmin(admin.ModelAdmin):
    list_display = ["existing_variation"]
    search_fields = ["existing_variation"]

admin.site.register(VEPAnnotationsExistingVariation, VEPAnnotationsExistingVariationAdmin)

class VEPAnnotationsPubmedAdmin(admin.ModelAdmin):
    list_display = ["pubmed_id"]
    search_fields = ["pubmed_id"]

admin.site.register(VEPAnnotationsPubmed, VEPAnnotationsPubmedAdmin)

class VEPAnnotationsClinvarAdmin(admin.ModelAdmin):
    list_display = ["clinvar_id", "clinvar_clinsig"]
    search_fields = ["clinvar_id"]

admin.site.register(VEPAnnotationsClinvar, VEPAnnotationsClinvarAdmin)

class GermlineVEPAnnotationsAdmin(admin.ModelAdmin):
    list_display = ["hgvsc", "hgvsp", "exon", "intron"]
    search_fields = ["hgvsc", "hgvsp"]

admin.site.register(GermlineVEPAnnotations, GermlineVEPAnnotationsAdmin)

class SomaticVEPAnnotationsAdmin(admin.ModelAdmin):
    list_display = ["hgvsc", "hgvsp", "exon", "intron"]
    search_fields = ["hgvsc", "hgvsp"]

admin.site.register(SomaticVEPAnnotations, SomaticVEPAnnotationsAdmin)

#TODO add the rest of the models and neaten up all the displays etc.