# Description:
# Pull out all samples of a specific panel from SVD and check how many have a certain variant
#
# Date: 23/03/23 - NT
# Use: python manage.py shell < /home/ew/somatic_db/queries/variant_percentage_check.py (with somatic_variant_db env activated)

from analysis.models import SampleAnalysis, Panel, VariantInstance


# Get all dna samples for the specified panel
panel_dna = Panel.objects.get(panel_name = 'GIST', assay = '1')
samples_dna = SampleAnalysis.objects.filter(panel = panel_dna)

panel_rna = Panel.objects.get(panel_name='GIST', assay = '2')
samples_rna = SampleAnalysis.objects.filter(panel = panel_rna)


dna_in_gene_count = 0
dna_without_gene_count = 0
rna_in_gene_count = 0
rna_without_gene_count = 0

sample_list = []

variants = VariantInstance.objects.filter(gene = 'PDGFRa')

for v in variants:
	sample_list.append(v.sample)

for entry in samples_dna:

	if entry.sample in sample_list:

		print(entry.sample)
		dna_in_gene_count += 1


	else:
		dna_without_gene_count += 1

for entry in samples_rna:

	if entry.sample in sample_list:

		print(entry.sample)
		rna_in_gene_count += 1

	else:
		rna_without_gene_count +=1

print(dna_in_gene_count)
print(dna_without_gene_count)

print('RNA')
print(rna_in_gene_count)
print(rna_without_gene_count)
	











		


#for entry in samples_dna:
	
#	print(entry.sample)
#	sample = entry.sample
#	print(entry.panel)
#	dna_sample_count += 1
	
#	variants = VariantInstance.objects.filter(gene = 'EGFR')
	
#	for v in variants:
#		if v.sample == sample:
	
#			print(sample)
#			dna_in_gene_count += 1
#			continue
#		continue

#for entry in samples_rna:
	
#	print(entry.sample)
#	sample = entry.sample
#	print(entry.panel)
#	rna_sample_count += 1
		
#	variants = VariantInstance.objects.filter(gene = 'EGFR')

#	for v in variants:
#		if v.sample == sample:

#			print(sample)
#			rna_in_gene_count += 1 
#			continue
#		continue

#print('Total DNA')
#print(dna_sample_count)
#print('Total RNA')
#print(rna_sample_count)
#print('DNA Count within gene')
#print(dna_in_gene_count)
#print('RNA Count within gene')
#print(rna_in_gene_count)





# Headers and liat to save output
#outlist = [['run', 'sample']]

# Get all samples in glioma dna panel
#glioma_panel_dna = Panel.objects.get(panel_name = 'Glioma', dna_or_rna = 'DNA')
#glioma_samples_dna = SampleAnalysis.objects.filter(panel = glioma_panel_dna)

# Loop through samples to get panel, sample and run
#for s in glioma_samples_dna:
#	outlist.append([str(s.worksheet.run),str(s.sample.sample_id)])

# Get all samples in glioma rna panel
#glioma_panel_rna = Panel.objects.get(panel_name = 'Glioma', dna_or_rna = 'RNA')
#glioma_samples_rna = SampleAnalysis.objects.filter(panel = glioma_panel_rna)

# Loop through samples to get panel, sample and run
#for s in glioma_samples_rna:
#        outlist.append([str(s.worksheet.run),str(s.sample.sample_id)])

# Output data to screen 
#for line in outlist:
#	print(','.join(line))
