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

admin.site.register(gene)
admin.site.register(coverage_regions)
admin.site.register(gene_coverage_analysis)
admin.site.register(coverage_regions_analysis)
admin.site.register(gaps_analysis)
admin.site.register(fusion)
admin.site.register(fusion_analysis)


