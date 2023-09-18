# Description:
# Get all checks of a specific variant (variant is genomic coord hardcoded in script)
# 
# Date: 04/10/2022
# Use: python manage.py shell < /home/ew/somatic_db/queries/all_dna_vars_since_date.py


from analysis.models import VariantInstance, VariantPanelAnalysis, Variant, VariantCheck, Check
from datetime import datetime

from_date = datetime(2023, 8, 11)

checks = Check.objects.filter(signoff_time__gt = from_date)
vars = []

for c in checks:
	sample_analysis = c.analysis
	panel_analysis = VariantPanelAnalysis.objects.filter(sample_analysis = sample_analysis)
	for v in panel_analysis:
		ws = sample_analysis.worksheet.ws_id
		sample = sample_analysis.sample.sample_id
		var = v.variant_instance.variant.variant
		hgvs_c = v.variant_instance.hgvs_c
		hgvs_p = v.variant_instance.hgvs_p
		svd_link = 'http://10.59.210.247:8000/analysis/' + str(sample_analysis.id)
		
		print(','.join([ws, sample, var, hgvs_c, hgvs_p, svd_link]))


#vars = VariantInstance.objects.all()

#for v in vars:
#    print(f'{v.variant.variant},{v.hgvs_c},{v.hgvs_p}')
