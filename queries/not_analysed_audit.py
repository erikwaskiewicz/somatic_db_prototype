# Description:
# Get all checks of a specific variant (variant is genomic coord hardcoded in script)
# 
# Date: 12/10/2023
# Use: python manage.py shell < /home/ew/somatic_db/queries/not_analysed_audit.py


from analysis.models import VariantInstance, VariantPanelAnalysis, Variant, VariantCheck

# get all variant instances
var_instances = VariantInstance.objects.all()

print('sample,ws,diagnostic,variant,status,all_checks,final_decision,PK')

# loop through instances of variant
for line in var_instances:

    try:
        var_panel_obj = VariantPanelAnalysis.objects.get(variant_instance = line)
        var_checks = VariantCheck.objects.filter(variant_analysis = var_panel_obj).order_by('pk')
        check_list = [v.get_decision_display() for v in var_checks]
        last_two = set(check_list[-2:])

        if last_two == set(['Not analysed']):

            # get sample metadata
            sample = line.sample.sample_id

            sample_analysis_obj = var_panel_obj.sample_analysis
            ws = sample_analysis_obj.worksheet
            diagnostic = str(ws.diagnostic)
            status = sample_analysis_obj.get_checks()['current_status']
            variant = str(line.variant.variant)
            pk = str(sample_analysis_obj.id)

            out = [sample, str(ws), diagnostic, variant, status, '|'.join(check_list), line.get_final_decision_display(), pk]
            print(','.join(out))

    except:
        #print(sample)
        pass

