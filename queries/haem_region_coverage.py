# Description
# Get regions with no coverage and less than 270x depth for myeloid and aml panels
# Genes - SRSF2, CEBPA
# utils.py - def create_myeloid_coverage_summary(sample_obj)

# Date 24/01/24
# Use: python manage.py shell < /home/ew/somatic_db/queries/haem_region_coverage.py (with somatic_variant_db env activate)

from analysis.models import RegionCoverageAnalysis, Panel, SampleAnalysis, Check, VariantInstance
from analysis.utils import create_myeloid_coverage_summary
from django.db.models import Q
from datetime import datetime
import pandas as pd

#MYELOID

# Get myeloid panel
panel = Panel.objects.get(panel_name = 'myeloid', assay = '1', genome_build='38')

# Regions with specific genes wanted
region_coverage = RegionCoverageAnalysis.objects.filter(Q(gene__gene__gene='SRSF2') | Q(gene__gene__gene='CEBPA'))
region_coverage = RegionCoverageAnalysis.objects.all()

# Get samples from panel
sample_obj = SampleAnalysis.objects.filter(panel=panel)

# Get the variant called
variant = VariantInstance.objects.all()

# Results within ~ last 6 months
#from_date = datetime(2023, 7, 1)

#checks = Check.objects.filter(signoff_time__gt = from_date)

# Genes of interest
genes = ['CEBPA', 'SRSF2']

# Create output lists
myeloid_sample_list = []
context_list = []
output_list = []
variant_list = []

#for c in checks:

for s in sample_obj:
	# 'CEBPA' or 'SRSF2' in create_myeloid_coverage_summary(s):
	myeloid_sample_list.append(s.sample.sample_id)

	if s.sample.sample_id in myeloid_sample_list:
		context_list.append([
			s.sample.sample_id,
			s.get_checks()['current_status'],
			'myeloid',
			s.worksheet.ws_id,
			s.worksheet.run,
			create_myeloid_coverage_summary(s)['summary_0x'],
			create_myeloid_coverage_summary(s)['summary_270x']
		])

for coverage in region_coverage:
	if  coverage.gene.sample.sample.sample_id in myeloid_sample_list:
		output_list.append([
			coverage.gene.sample.sample.sample_id,
			coverage.gene.gene.gene,
			coverage.chr_start,
			coverage.pos_start,
			coverage.chr_end,
			coverage.pos_end
		])

for v in variant:
	if v.sample.sample_id in myeloid_sample_list and v.gene in genes:
		variant_list.append([
			v.sample.sample_id,
			v.variant.variant,
			v.hgvs_c,
			v.final_decision
		])

		
myeloid_context_list = pd.DataFrame(context_list, columns = ['sample', 'status', 'panel', 'ws', 'run', '0x', '270x'])
myeloid_outlist = pd.DataFrame(output_list, columns = ['sample', 'gene', 'chr start', 'pos start', 'chr end', 'pos end'])
myeloid_with_variants = pd.DataFrame(variant_list, columns = ['sample', 'variant', 'hgvsc', 'decision'])

myeloid_combine = pd.merge(myeloid_outlist, myeloid_context_list, on = 'sample')
myeloid_add_variants = pd.merge(myeloid_combine, myeloid_outlist, on = 'sample')
print(myeloid_add_variants)
myeloid_add_variants.to_csv('myeloid_regions.csv')
