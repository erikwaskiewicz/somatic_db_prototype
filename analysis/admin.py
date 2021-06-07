from django.contrib import admin
from .models import *


admin.site.register(Run)
admin.site.register(Worksheet)
admin.site.register(Sample)
admin.site.register(Panel)
admin.site.register(SampleAnalysis)
admin.site.register(Check)
admin.site.register(variant_call)
admin.site.register(variant_analysis)
admin.site.register(polys)
admin.site.register(gene)
admin.site.register(coverage_regions)
admin.site.register(gene_coverage_analysis)
admin.site.register(coverage_regions_analysis)
admin.site.register(gaps_analysis)


