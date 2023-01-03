# Description:
# Get all checks of a specific variant (variant is genomic coord hardcoded in script)
# 
# Date: 04/10/2022
# Use: python manage.py shell < /home/ew/somatic_db/queries/all_variants_in_gene.py


from analysis.models import VariantInstance, VariantPanelAnalysis, Variant, VariantCheck

gene = 'SF3B1'

vars = VariantInstance.objects.filter(gene = gene)

for v in vars:
    print(f'{v.variant.genomic_37},{v.hgvs_c},{v.hgvs_p}')
