# Description:
# Pull out all individual checks between two dates, date range hardcoded in script
# 
# Date: 10/01/2023 - NT
# Use: python manage.py shell < /home/ew/somatic_db/queries/tp53_query.py (with somatic_variant_db env activated)


import datetime
from analysis.models import SampleAnalysis, VariantInstance, Sample, VariantToVariantList
from django.contrib.humanize.templatetags.humanize import ordinal


# headers and list to save output
out_list = [['Sample', 'Poly?', 'Variant', 'hgvs_c', 'hgvs_p', 'Worksheet', 'Final Decision']]

# all sample analysis objects where panel is myeloid
samples = SampleAnalysis.objects.filter(panel__panel_name="myeloid")

for sample in samples:
	
	# just variants for one sample analysis
	variants = VariantInstance.objects.filter(sample=sample.sample)
	
	for v in variants:
	
		# getting genes that = TP53 with/without a poly 
		if v.gene == 'TP53':

			poly = "False"
		
			# check if on poly variant list
			for l in VariantToVariantList.objects.filter(variant=v.variant):	

				if l.variant_list.name == "TSO500_polys":

					poly = "True"

			# getting the sample id 
			sample_id = v.sample.sample_id
		
			# getting the variants 
			variant = v.variant.genomic_37
			
			# hgvs coding annotation
			hgvs_c = v.hgvs_c

			# hgvs protein annotation
			hgvs_p = v.hgvs_p

			# get worksheet
			worksheet = sample.worksheet.ws_id
			
			# get final decision (genuine or not)
			final_decision = v.final_decision
			
			# only append if poly is false
			if poly == "False":
		
				out_list.append([
					sample_id,
					poly,
					variant,
					hgvs_c,
					hgvs_p,
					worksheet,
					final_decision
					])
	
# print to screen (can redirect to file in shell)
for line in out_list:
    print(','.join(line))
