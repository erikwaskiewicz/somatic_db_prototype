# Description:
# Get all checks of a specific variant (variant is genomic coord hardcoded in script)
# 
# Date: 04/10/2022
# Use: python manage.py shell < /home/ew/somatic_db/queries/myeloid_bug.py


from analysis.models import VariantInstance, VariantPanelAnalysis, Variant, VariantCheck

# define variant of interest
#variant = '7:148543693T>A'
variant = '7:148543693TAA>-'

# get variant object and find all instances of it
variant_obj = Variant.objects.get(genomic_37 = variant)
var_instances = VariantInstance.objects.filter(variant = variant_obj)

# headers and list to store output
out_list = [['variant', 'sample', 'ws', 'panel', 'check', 'user', 'decision', 'comment']]

# loop through instances of variant
for line in var_instances:

    # get sample metadata
    sample = line.sample.sample_id

    var_panel_obj = VariantPanelAnalysis.objects.get(variant_instance = line)
    sample_analysis_obj = var_panel_obj.sample_analysis

    ws = str(sample_analysis_obj.worksheet)
    panel = sample_analysis_obj.panel.panel_name

    # loop through each check for the instance of the variant and output all
    for n, check in enumerate(sample_analysis_obj.get_checks()['all_checks']):

        user = str(check.user)

        var_check = VariantCheck.objects.get(variant_analysis = var_panel_obj, check_object = check)
        decision = var_check.get_decision_display()
        comment = var_check.comment
        if comment == None:
            comment = ''

        out_list.append([variant, sample, ws, panel, str(n+1), user, decision, comment])


# print to screen (can be redirected in shell)
for line in out_list:
    print('\t'.join(line))
