# Description:
# Pull out all glioma samples in SVD and add info requested by Rhianedd 19/06/2023
#
# Date: 19/06/23 - EW
# Use: python manage.py shell < /home/ew/somatic_db/queries/glioma_dna.py (with somatic_variant_db env activated)

from analysis.models import SampleAnalysis, Panel, VariantPanelAnalysis, GeneCoverageAnalysis, Gene


gene_list = ['IDH1', 'IDH2', 'BRAF', 'EGFR', 'ATRX', 'H3F3A', 'TERT', 'PTEN', 'TP53', 'CDKN2A']


# Headers and list to save output
headers = ['Lab no.', 'WS', 'Patient name', 'QC']
for gene in gene_list:
	headers.append(gene)
headers.append('Other calls')
for gene in gene_list:
	headers.append(f'{gene} 270x')
	headers.append(f'{gene} 135x')
headers.append('Run ID')
headers.append('SVD link')

outlist = [headers]


# Get all samples in glioma dna panel
glioma_panel = Panel.objects.get(panel_name = 'Glioma', assay = '1', version=1, genome_build=37)
glioma_samples = SampleAnalysis.objects.filter(panel = glioma_panel)

# Loop through samples to get panel, sample and run
for s in glioma_samples:
	if not s.worksheet.diagnostic:
		continue
	if s.get_checks()['current_status'] not in ['Complete', 'Fail']:
		continue

	if s.get_checks()['current_status'] == 'Fail':
		print(s.sample.sample_id, f'http://10.59.210.247:8000/analysis/{s.id}')
		for n, c in enumerate(s.get_checks()['all_checks']):
			print(str(n+1), c.user, c.overall_comment)
		print('')

	# empty variables for outputs
	vars = {}
	other = []

	cov_135 = {}
	cov_270 = {}

	panel = VariantPanelAnalysis.objects.filter(sample_analysis=s)
	for v in panel:
		genes = v.variant_instance.gene
		try:
			hgvs =  v.variant_instance.hgvs_c.split(':')[1]
		except:
			hgvs = ''
		genuine = v.variant_instance.get_final_decision_display()

		if genuine not in ['Genuine', 'Miscalled']:
			if 'TERT' in genes:
				other.append(f'{genes} {v.variant_instance.variant.variant} ({genuine})')
			else:
				other.append(f'{genes} {hgvs} ({genuine})')
		else:
			for gene in gene_list:
				if gene in genes:

					if gene == 'TERT':
						try:
							vars[gene].append(f'{v.variant_instance.variant.variant} ({genuine})')
						except KeyError:
							vars[gene] = [f'{v.variant_instance.variant.variant} ({genuine})']
					else:
						try:
							vars[gene].append(f'{hgvs} ({genuine})')
						except KeyError:
							vars[gene] = [f'{hgvs} ({genuine})']


	for gene in gene_list:
		gene_obj = Gene.objects.get(gene = gene)
		try:
			gene_cov_obj = GeneCoverageAnalysis.objects.get(sample = s, gene = gene_obj)
			cov_135[gene] = str(gene_cov_obj.percent_135x) + '%'
			cov_270[gene] = str(gene_cov_obj.percent_270x) + '%'
		except:
			cov_135[gene] = ''
			cov_270[gene] = ''


	# make list to  add to output
	# first few columns
	temp_out = [s.sample.sample_id, s.worksheet.ws_id, s.sample.sample_name, s.get_checks()['current_status']]

	# vars per gene
	for gene in gene_list:
		try:
			temp_out.append(','.join(vars[gene]))
		except KeyError:
			temp_out.append('WT')
	temp_out.append(','.join(other))

	# cov per gene
	for gene in gene_list:
		temp_out.append(cov_270[gene])
		temp_out.append(cov_135[gene])

	# last few columns
	temp_out.append(s.worksheet.run.run_id)
	temp_out.append(f'http://10.59.210.247:8000/analysis/{s.id}')

	outlist.append(temp_out)

# Output data to screen 
#for line in outlist:
#	print('\t'.join(line))



