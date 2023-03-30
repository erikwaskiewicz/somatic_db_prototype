# Description:
# Script to fix manually entered variant depth. Accidentally set as 0
# 
# Date: 19/01/2023 - KM
# Use: python manage.py shell < /home/ew/somatic_db/queries/vaf_fix.py (with somatic_variant_db env activated)


from analysis.models import SampleAnalysis, VariantInstance, Sample, VariantToVariantList
from django.contrib.humanize.templatetags.humanize import ordinal

# just variants for one sample analysis
samples = SampleAnalysis.objects.all()

variants = VariantInstance.objects.all()

for sample in samples:

	variants = VariantInstance.objects.all()

	for v in variants:
	
		if v.variant.genomic_37 == "7:140453155C>A":

			print(v.sample)
	

