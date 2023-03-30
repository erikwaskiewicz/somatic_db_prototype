# Description:
# Script to fix manually entered variant depth. Accidentally set as 0
# 
# Date: 18/01/2023 - SS
# Use: python manage.py shell < /home/ew/somatic_db/queries/vaf_fix.py (with somatic_variant_db env activated)


from analysis.models import SampleAnalysis, VariantInstance, Sample, VariantToVariantList
from django.contrib.humanize.templatetags.humanize import ordinal

# just variants for one sample analysis
variants = VariantInstance.objects.filter(sample__sample_id="23M04046")
	
for v in variants:

	if v.variant.genomic_37 == "g.7578500_7578502delinsACAGGGAC":
		#v.alt_count_ntc = 0
		#v.total_count_ntc = 0
		#v.total_count = 198
		#v.in_ntc = False
		v.alt_count = 92
		v.save()
	

