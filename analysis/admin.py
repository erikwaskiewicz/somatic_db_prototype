from django.contrib import admin
from .models import *


admin.site.register(Run)
admin.site.register(Worksheet)
admin.site.register(Sample)
admin.site.register(Panel)
admin.site.register(SampleAnalysis)
admin.site.register(Check)
admin.site.register(Variant)
admin.site.register(VariantAnalysis)
admin.site.register(VariantList)
admin.site.register(VariantToVariantList)
admin.site.register(VariantCheck)

admin.site.register(Gene)
admin.site.register(CoverageRegions)
admin.site.register(GeneCoverageAnalysis)
admin.site.register(CoverageRegionsAnalysis)
admin.site.register(GapsAnalysis)
admin.site.register(Fusion)
admin.site.register(FusionAnalysis)


