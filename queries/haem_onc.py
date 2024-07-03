# Description
# Sample Id, c., p., variant, worksheet, run, VAF, no. reads, panel for myeloid, MPN and CLL 
#
# SampleAnalysis - worksheet, sample, panel, total_reads
# VariantInstance - variant, hgvs_c, hgvs_p, vaf
# Panel - panel_id
# 
# Date 11/05/23 - NT
# Use: python manage.py shell < /home/ew/somatic_db/queries/haem_onc.py (with somatic_variant_db env activate)

from analysis.models import SampleAnalysis, VariantInstance, Panel, VariantCheck
from django.contrib.humanize.templatetags.humanize import ordinal
from django.db.models import Q
import pandas as pd

# Myeloid panel
myeloid_panel_obj = Panel.objects.get(panel_name = 'myeloid')
myeloid_samples = SampleAnalysis.objects.filter(panel = myeloid_panel_obj)

myeloid_variant_sample_obj = VariantInstance.objects.all()

myeloid_comment_obj = VariantCheck.objects.all()

# Loop through samples and pull out data
myeloid_sample_list = []
myeloid_outlist = []
myeloid_variant_list = []
myeloid_comment = []

for v in myeloid_variant_sample_obj:
	myeloid_sample_list.append(v.sample.sample_id)

	if v.sample.sample_id in myeloid_sample_list:
		myeloid_variant_list.append([v.sample.sample_id
			, v.gene
			, v.variant.variant
			, v.hgvs_p
			, v.hgvs_c
			, v.total_count
			, v.vaf()])
		 	
for s in myeloid_samples:
	if s.sample.sample_id in myeloid_sample_list:
		myeloid_outlist.append([s.sample.sample_id
			, s.panel.panel_name
			, s.worksheet.ws_id
			, s.worksheet.run.run_id])
	else:
		print('fuck')

for c in myeloid_comment_obj:
	if c.variant_analysis.sample_analysis.sample.sample_id in myeloid_sample_list:
		myeloid_comment.append([c.variant_analysis.sample_analysis.sample.sample_id,
			, c.decision
			, c.comment
			, c.comment_updated])

myeloid_variant_df = pd.DataFrame(myeloid_outlist, columns = ['sample', 'panel', 'worksheet', 'run'])

myeloid_sample_df = pd.DataFrame(myeloid_variant_list, columns = ['sample', 'gene', 'variant', 'hgvs_p', 'hgvs_c', 'total_reads', 'vaf'])	

myeloid_comment_df pd.DataFrame(myeloid_variant_list, columns = ['sample', 'decision', 'comment', 'comment_updated'])

myeloid_first = pd.merge(myeloid_variant_df, myeloid_sample_df, on='sample')

myeloid_final = pd.merge(myeloid_first, myeloid_comment_df, on='sample')



# MPN panel
mpn_panel_obj = Panel.objects.get(panel_name = 'mpn')
mpn_samples = SampleAnalysis.objects.filter(panel = mpn_panel_obj)

mpn_variant_sample_obj = VariantInstance.objects.all()

# Loop through samples and pull out data
mpn_sample_list = []
mpn_outlist = []
mpn_variant_list = []

for v in mpn_variant_sample_obj:
	mpn_sample_list.append(v.sample.sample_id)

	if v.sample.sample_id in mpn_sample_list:
		mpn_variant_list.append([v.sample.sample_id
			, v.gene
			, v.variant.variant
			, v.hgvs_p
			, v.hgvs_c
			, v.total_count
			, v.vaf()])

for s in mpn_samples:
	if s.sample.sample_id in mpn_sample_list:
		mpn_outlist.append([s.sample.sample_id
			, s.panel.panel_name
			, s.worksheet.ws_id
			, s.worksheet.run.run_id])
	else:
		print('fuck')

mpn_variant_df = pd.DataFrame(mpn_outlist, columns = ['sample', 'panel', 'worksheet', 'run'])

mpn_sample_df = pd.DataFrame(mpn_variant_list, columns = ['sample', 'gene', 'variant', 'hgvs_p', 'hgvs_c', 'total_reads', 'vaf'])

mpn_final = pd.merge(mpn_variant_df, mpn_sample_df, on='sample')


# CLL panel
cll_panel_obj = Panel.objects.get(panel_name = 'cll')
cll_samples = SampleAnalysis.objects.filter(panel = cll_panel_obj)

cll_variant_sample_obj = VariantInstance.objects.all()

# Loop through samples and pull out data
cll_sample_list = []
cll_outlist = []
cll_variant_list = []

for v in cll_variant_sample_obj:
	cll_sample_list.append(v.sample.sample_id)

	if v.sample.sample_id in cll_sample_list:
		cll_variant_list.append([v.sample.sample_id
			, v.gene
			, v.variant.variant
			, v.hgvs_p
			, v.hgvs_c
			, v.total_count
			, v.vaf()])
	
for s in cll_samples:
	if s.sample.sample_id in cll_sample_list:
		cll_outlist.append([s.sample.sample_id
			, s.panel.panel_name
			, s.worksheet.ws_id
			, s.worksheet.run.run_id])
	else:
		print('fuck')
	
cll_variant_df = pd.DataFrame(cll_outlist, columns = ['sample', 'panel', 'worksheet', 'run'])

cll_sample_df = pd.DataFrame(cll_variant_list, columns = ['sample', 'gene', 'variant', 'hgvs_p', 'hgvs_c', 'total_reads', 'vaf'])

cll_final = pd.merge(cll_variant_df, cll_sample_df, on='sample')


# Put all dataframes into one
myeloid_mpn_df = myeloid_final.append(mpn_final, ignore_index=True)
all_df = myeloid_mpn_df.append(cll_final, ignore_index=True)
print(all_df)
all_df.to_csv('haem_onc.csv')
