# Description:
# Script to fix manually entered variant depth. Accidentally set as 0
# 
# Date: 19/01/2023 - KM
# Use: python manage.py shell < /home/ew/somatic_db/queries/vaf_fix.py (with somatic_variant_db env activated)


from analysis.models import SampleAnalysis, VariantInstance, Sample, VariantToVariantList, VariantPanelAnalysis
from django.contrib.humanize.templatetags.humanize import ordinal

# just variants for one sample analysis
samples = SampleAnalysis.objects.all()

variants = VariantInstance.objects.all()

for sample in samples:

	variants = VariantInstance.objects.filter(sample = sample.sample)

	for v in variants:
	
		if v.variant.variant == "X:40073237G>GAGACC":

			print(sample.sample.sample_id)

			#Get IGV checks
			variant_panel_analysis = VariantPanelAnalysis.objects.filter(sample_analysis = sample, variant_instance = v)

			for instance in variant_panel_analysis:

				checks = instance.get_all_checks()

				for i in checks:

					print(i.decision)

