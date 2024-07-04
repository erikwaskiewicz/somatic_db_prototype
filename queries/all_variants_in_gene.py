# Description:
# Get all checks of a specific variant (variant is genomic coord hardcoded in script)
# 
# Date: 04/10/2022
# Use: python manage.py shell < /home/ew/somatic_db/queries/all_variants_in_gene.py


from analysis.models import VariantInstance, VariantPanelAnalysis, Variant, VariantCheck

gene = 'SRSF2'

vars = VariantInstance.objects.filter(gene = gene)



for v in vars:

    try:
        panel = VariantPanelAnalysis.objects.get(variant_instance = v)

        comment = ''
        comment_objs = VariantCheck.objects.filter(variant_analysis = panel)
        for c in comment_objs:
            if c.comment:
                comment_formatted = c.comment.strip().replace("\t", " ").replace("\r", " ").replace("\n", " ")
                comment += f'{comment_formatted}; '

        print(f'{panel.sample_analysis.worksheet.run}\t{panel.sample_analysis.worksheet}\t{panel.sample_analysis.sample.sample_id}\t{panel.sample_analysis.panel}\t{gene}\t{v.variant.variant}\t{v.hgvs_c}\t{v.hgvs_p}\t{v.vaf()}\t{v.get_final_decision_display()}\t{comment}')
    except:
        pass
