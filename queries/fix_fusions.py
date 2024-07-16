# Description:
# Seperator for fusions can be a mix of -, -- or /, should always be - for consistency
# 
# Date: 7/2/2024
# Use: python manage.py shell < /home/ew/somatic_db/queries/fix_fusions.py


from analysis.models import FusionAnalysis, Fusion

all_fusions = FusionAnalysis.objects.filter(fusion_caller = 'Fusion')

for f in all_fusions:

    genes = f.fusion_genes.fusion_genes
    if '/' in genes or '--' in genes:
        new_genes = genes.replace('/', '-').replace('--', '-')

        print(genes, new_genes)

        #new_genes_obj, created = Fusion.objects.get_or_create(
        #    fusion_genes = new_genes,
        #    left_breakpoint = f.fusion_genes.left_breakpoint,
        #    right_breakpoint = f.fusion_genes.right_breakpoint,
        #    genome_build = f.fusion_genes.genome_build
        #)

        #print(genes, new_genes, new_genes_obj, created)

        #f.fusion_genes = new_genes_obj
        #f.fusion_genes.save()




# remove old fusion objects that are no longer related to any analyses
all_fusions = Fusion.objects.all()

for f in all_fusions:
    if ' ' not in f.fusion_genes:
        if ('/' in f.fusion_genes) or ('--' in f.fusion_genes):
            print(f.fusion_genes)
            for fa in FusionAnalysis.objects.filter(fusion_genes = f):
                print(fa)

