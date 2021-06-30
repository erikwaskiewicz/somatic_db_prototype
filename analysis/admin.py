from django.contrib import admin
from .models import *


admin.site.register(Run)
admin.site.register(Worksheet)
admin.site.register(Sample)
admin.site.register(Panel)
admin.site.register(SampleAnalysis)
admin.site.register(Check)
admin.site.register(Variant)
admin.site.register(VariantInstance)
admin.site.register(VariantPanelAnalysis)
admin.site.register(VariantList)
admin.site.register(VariantToVariantList)
admin.site.register(VariantCheck)

admin.site.register(Gene)
admin.site.register(GeneCoverageAnalysis)
admin.site.register(RegionCoverageAnalysis)
admin.site.register(GapsAnalysis)
admin.site.register(Fusion)
admin.site.register(FusionAnalysis)
admin.site.register(FusionCheck)
admin.site.register(FusionPanelAnalysis)


