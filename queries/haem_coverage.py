# Description
# Get regions with no coverage and less than 270x depth for myeloid and aml panels
# Genes - NPM1, SRSF2, RUNX1, CEBPA
# utils.py - def create_myeloid_coverage_summary(sample_obj)

# Date 19/12/23
# Use: python manage.py shell < /home/ew/somatic_db/queries/haem_coverage.py (with somatic_variant_db env activate)

from analysis.models import Panel, GeneCoverageAnalysis, RegionCoverageAnalysis, VariantInstance, SampleAnalysis, VariantCheck, Check
from django.contrib.humanize.templatetags.humanize import ordinal
import pandas as pd
from django.utils import timezone
from analysis.utils import create_myeloid_coverage_summary
from datetime import datetime
import csv
from django.db.models import Q
import numpy as np

# Past six months
from_date = datetime(2023, 6, 1)

# FOR BUILD 37

#output_list_37 = []
#gene_variant_list_37 = []
#myeloid_sample_list_37 = []
#myeloid_comment_list_37 = []

checks = Check.objects.filter(signoff_time__gt = from_date)

genes = ['CEPBA','SRSF2', 'NPM1']

#for c in checks:
#	# Myeloid panel
#	myeloid_panel_obj_37 = Panel.objects.get(panel_name = 'myeloid', assay = '1', genome_build='37')
#	sample_obj_37 = SampleAnalysis.objects.filter(panel = myeloid_panel_obj_37)
#	variants = VariantInstance.objects.all()
#	myeloid_comment_obj = VariantCheck.objects.all()

#for s in sample_obj_37:
#	if 'CEPBA' or 'SRSF2' or 'NPM1' in create_myeloid_coverage_summary(s):
#		myeloid_sample_list_37.append(s.sample.sample_id)

#	if s.sample.sample_id in myeloid_sample_list_37:
#		output_list_37.append([
#		s.sample.sample_id,
#		s.get_checks()['current_status'],
#		'myeloid',
#		s.worksheet.ws_id,
#		s.worksheet.run, 
#		create_myeloid_coverage_summary(s)['summary_0x'],
#		create_myeloid_coverage_summary(s)['summary_270x']
#		])

#for v in variants:
#	if v.sample.sample_id in myeloid_sample_list_37 and v.gene in genes:
#		gene_variant_list_37.append([
#		v.sample.sample_id,
#		v.gene,
#		v.variant.variant
#		])

#for c in myeloid_comment_obj:
 #       if c.variant_analysis.sample_analysis.sample.sample_id in myeloid_sample_list_37:
  #              myeloid_comment_list_37.append([c.variant_analysis.sample_analysis.sample.sample_id
   #                     , c.comment])

#myeloid_outlist_37 = pd.DataFrame(output_list_37, columns = ['sample', 'status', 'panel', 'ws', 'run', '0x', '270x'])
#myeloid_variants_37 = pd.DataFrame(gene_variant_list_37, columns = ['sample', 'gene', 'variant'])
#myeloid_comment_37 = pd.DataFrame(myeloid_comment_list_37, columns = ['sample', 'comment'])
#myeloid_first_37 = pd.merge(myeloid_outlist_37, myeloid_variants_37, on = 'sample')
#myeloid_final_37 = pd.merge(myeloid_first_37, myeloid_comment_37, on = 'sample')
#myeloid_final_37.drop_duplicates()
#myeloid_final_37.to_csv('myeloid_37_comment.csv')

# FOR BUILD 38

output_list_38 = []
gene_variant_list_38 = []
myeloid_sample_list_38 = []
myeloid_comment_list_38 = []

for c in checks:
        # Myeloid panel b38
        myeloid_panel_obj_38 = Panel.objects.get(panel_name = 'myeloid', assay = '1', genome_build='38')
        sample_obj_38 = SampleAnalysis.objects.filter(panel = myeloid_panel_obj_38)
        variants = VariantInstance.objects.all()
        myeloid_comment_obj = VariantCheck.objects.all()

for s in sample_obj_38:
        if 'CEPBA' or 'SRSF2' or 'NPM1' in create_myeloid_coverage_summary(s):
                myeloid_sample_list_38.append(s.sample.sample_id)

        if s.sample.sample_id in myeloid_sample_list_38:
                output_list_38.append([
                s.sample.sample_id,
                s.get_checks()['current_status'],
                'myeloid',
                s.worksheet.ws_id,
                s.worksheet.run,
                create_myeloid_coverage_summary(s)['summary_0x'],
                create_myeloid_coverage_summary(s)['summary_270x']
                ])

for v in variants:
        if v.sample.sample_id in myeloid_sample_list_38 and v.gene in genes:
                gene_variant_list_38.append([
                v.sample.sample_id,
                v.gene,
                v.variant.variant
                ])

for c in myeloid_comment_obj:
        if c.variant_analysis.sample_analysis.sample.sample_id in myeloid_sample_list_38:
                myeloid_comment_list_38.append([c.variant_analysis.sample_analysis.sample.sample_id
                        , c.comment])

myeloid_outlist_38 = pd.DataFrame(output_list_38, columns = ['sample', 'status', 'panel', 'ws', 'run', '0x', '270x'])
myeloid_variants_38 = pd.DataFrame(gene_variant_list_38, columns = ['sample', 'gene', 'variant'])
myeloid_comment_38 = pd.DataFrame(myeloid_comment_list_38, columns = ['sample', 'comment'])
myeloid_first_38 = pd.merge(myeloid_outlist_38, myeloid_variants_38, on = 'sample')
myeloid_final_38 = pd.merge(myeloid_first_38, myeloid_comment_38, on = 'sample')
myeloid_final_38.drop_duplicates()
myeloid_final_38.to_csv('myeloid_38_comment.csv')



