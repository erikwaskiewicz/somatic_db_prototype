# Description:
# Pull out all glioma samples in SVD and add info requested by Rhianedd 19/06/2023
#
# Date: 19/06/23 - EW
# Use: python manage.py shell < /home/ew/somatic_db/queries/glioma_rna.py (with somatic_variant_db env activated)

from analysis.models import SampleAnalysis, Panel, VariantPanelAnalysis, FusionPanelAnalysis

# Headers and list to save output
outlist = [['Lab no.', 'WS', 'Patient name', 'QC', 'BRAF', 'EGFR', 'NTRK1', 'NTRK2', 'NTRK3', 'Other calls', 'No. reads', 'Run ID', 'SVD link']]

# Get all samples in glioma dna panel
glioma_panel_rna = Panel.objects.get(panel_name = 'Glioma', assay = '2', version=1, genome_build=37)
glioma_samples_rna = SampleAnalysis.objects.filter(panel = glioma_panel_rna)

# Loop through samples to get panel, sample and run
for s in glioma_samples_rna:
	if not s.worksheet.diagnostic:
		continue
	if s.get_checks()['current_status'] not in ['Complete', 'Fail']:
		continue

	#if s.get_checks()['current_status'] == 'Fail':
	#	print(s.sample.sample_id, f'http://10.59.210.247:8000/analysis/{s.id}')
	#	for n, c in enumerate(s.get_checks()['all_checks']):
	#		print(str(n+1), c.user, c.overall_comment)
	#	print('')

	# get fusions and split by gene
	braf = []
	egfr = []
	ntrk1 = []
	ntrk2 = []
	ntrk3 = []
	other = []

	panel = FusionPanelAnalysis.objects.filter(sample_analysis=s)
	for v in panel:
		genes = v.fusion_instance.fusion_genes.fusion_genes
		genuine = v.fusion_instance.get_final_decision_display()
		if genuine not in ['Genuine', 'Miscalled']:
			other.append(f'{genes} ({genuine})')
		elif 'BRAF' in genes:
			braf.append(f'{genes} ({genuine})')
		elif 'EGFR' in genes:
			egfr.append(f'{genes} ({genuine})')
		elif 'NTRK1' in genes:
			ntrk1.append(f'{genes} ({genuine})')
		elif 'NTRK2' in genes:
			ntrk2.append(f'{genes} ({genuine})')
		elif 'NTRK3' in genes:
			ntrk3.append(f'{genes} ({genuine})')

	if len(braf) == 0:
		braf.append('WT')
	if len(egfr) == 0:
		egfr.append('WT')
	if len(ntrk1) == 0:
		ntrk1.append('WT')
	if len(ntrk2) == 0:
		ntrk2.append('WT')
	if len(ntrk3) == 0:
		ntrk3.append('WT')


	outlist.append([
		s.sample.sample_id, 
		s.worksheet.ws_id,
		s.sample.sample_name,
		s.get_checks()['current_status'],
		','.join(braf),
		','.join(egfr),
		','.join(ntrk1),
		','.join(ntrk2),
		','.join(ntrk3),
		','.join(other),
		str(s.total_reads),
		s.worksheet.run.run_id,
		f'http://10.59.210.247:8000/analysis/{s.id}',
	])

# Output data to screen 
for line in outlist:
	print('\t'.join(line))



