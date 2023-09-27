# Description:
# Pull out all KRAS variants and work out proportion G12C, request from Dr Craig Barrington 10/07/2023
#
# Date: 10/07/23 - EW
# Use: python manage.py shell < /home/ew/somatic_db/queries/craig_query.py (with somatic_variant_db env activated)

from analysis.models import SampleAnalysis, Panel, VariantPanelAnalysis, FusionPanelAnalysis

# Headers and list to save output
outlist = []

# Get all samples in glioma dna panel
panel = Panel.objects.get(panel_name = 'Colorectal', assay = '1', version=1, genome_build=37)
samples = SampleAnalysis.objects.filter(panel = panel)

# Loop through samples to get panel, sample and run
for s in samples:
	if not s.worksheet.diagnostic:
		continue
	if s.get_checks()['current_status'] not in ['Complete']:
		continue

	panel_analysis = VariantPanelAnalysis.objects.filter(sample_analysis=s)
	for v in panel_analysis:
		if v.variant_instance.gene == 'KRAS':

			outlist.append([
				s.sample.sample_id, 
				s.worksheet.run.run_id,
				v.variant_instance.variant.variant,
				v.variant_instance.hgvs_c,
				v.variant_instance.hgvs_p,
			])

# Output data to screen 
for line in outlist:
	print('\t'.join(line))



