# Testing coverage of SRSF2 and CEBPA for test runs that were designed to improve coverage. 
# Genes - SRSF2, CEBPA
# utils.py - def create_myeloid_coverage_summary(sample_obj)

# Date 24/01/24
# Use: python manage.py shell < /home/ew/somatic_db/queries/haem_cov_test.py (with somatic_variant_db env activated

from analysis.models import GeneCoverageAnalysis, Panel, SampleAnalysis, Check, VariantInstance
from analysis.utils import create_myeloid_coverage_summary
from django.db.models import Q
from datetime import datetime
import pandas as pd

#MYELOID

# Get myeloid panel
panel = Panel.objects.get(panel_name = 'myeloid', assay = '1', genome_build='38')

# Get test worksheets
gene_obj_rerun = GeneCoverageAnalysis.objects.filter(sample__worksheet__ws_id='23-6244_R')
#sample_obj = SampleAnalysis.objects.filter(panel=panel, Q(worksheet__worksheet__ws_id='23-644R') | Q(worksheet__worksheet__ws_id='23-643R'))

# Get variant and gene
variants = VariantInstance.objects.filter(Q(gene='SFSF2') | Q(gene='CEBPA'))

# Lists
rerun_list = []
orig_list = []

for g in gene_obj_rerun:
#	if g.gene.gene == 'SRSF2' or g.gene.gene == 'CEBPA':	
	rerun_list.append([
		g.sample.worksheet.ws_id,
		g.sample.sample.sample_id,
		g.gene.gene,
		g.percent_270x
	])

#print(rerun_list)
	
gene_obj_orig = GeneCoverageAnalysis.objects.filter(sample__worksheet__ws_id='23-6244')

for g in gene_obj_orig:
#        if g.gene.gene == 'SRSF2' or g.gene.gene == 'CEBPA':
	orig_list.append([
		g.sample.worksheet.ws_id,
		g.sample.sample.sample_id,
		g.gene.gene,
		g.percent_270x
	])

#print(orig_list)

	
rerun_df = pd.DataFrame(rerun_list, columns = ['worksheet', 'sample', 'gene', 'percent_270x'])
orig_df = pd.DataFrame(orig_list, columns = ['worksheet', 'sample', 'gene', 'percent_270x'])

merged = rerun_df.merge(orig_df, on = ['sample', 'gene'])
print(merged)
merged.to_csv('haem_cov_rerun.csv')
