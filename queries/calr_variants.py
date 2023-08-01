# Description:
# Get all checks of a specific variant (variant is genomic coord hardcoded in script)
# 
# Date: 04/10/2022
# Use: python manage.py shell < /home/ew/somatic_db/queries/all_variants_in_gene.py


from analysis.models import VariantInstance, VariantPanelAnalysis, Variant, VariantCheck

gene = 'CALR'

vars = VariantInstance.objects.filter(gene = gene)
headers = ['status', 'sample', 'ws', 'panel', 'run', 'svd_link', 'gene', 'genomic', 'c.', 'p.', 'vaf', 'final_decision', 'check1_decision', 'check1_comments', 'check2_decision', 'check2_comments', 'check3_decision']
print('\t'.join(headers))

#ADD run and SVD link

for v in vars:
	genomic = v.variant.variant
	hgvs_c = v.hgvs_c
	hgvs_p = v.hgvs_p
	vaf = str(v.vaf())
	gene = v.gene
	final_call = v.get_final_decision_display()

	sample = v.sample.sample_id
	panel_analysis = VariantPanelAnalysis.objects.get(variant_instance = v)
	sample_analysis = panel_analysis.sample_analysis

	svd_link = f'http://10.59.210.247:8000/analysis/{sample_analysis.id}'
	status = sample_analysis.get_checks()['current_status']
	worksheet = sample_analysis.worksheet
	panel = sample_analysis.panel.pretty_print
	run = worksheet.run.run_id

	out = [status, sample, worksheet.ws_id, panel, run, svd_link, gene, genomic, hgvs_c, hgvs_p, vaf, final_call]

	all_checks = VariantCheck.objects.filter(variant_analysis = panel_analysis)
	for c in all_checks:
		out.append(c.get_decision_display())
		if c.comment:
			print(c.comment.rstrip().replace('\t', ' ').replace('\n', ' '))
			out.append(c.comment.rstrip().replace('\t', ' ').replace('\n', ' '))
		else:
			out.append('')
	#print('\t'.join(out))

