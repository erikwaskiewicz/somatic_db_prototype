# Description:
# script to pull out the coverage statement produced for myeloid referrals in all samples
# was created in response to incident CG-22-274-GEN, script was run before and after chnages to the script and outputs compared
#
# Date: 30/09/2022 - EW
# Use: python manage.py shell < /home/ew/somatic_db/queries/myeloid_bug.py (with somatic_variant_db env activated)


from analysis.models import SampleAnalysis, Panel
from analysis.utils import create_myeloid_coverage_summary


# headers and list to store output
output_list = [['pk', 'status', 'sample', 'panel', 'ws', 'run', 'new_0x', 'new_270x']]


# get all samples in myeloid panel
myeloid_panel_obj = Panel.objects.get(panel_name = 'myeloid', version = '1', genome_build = '37', assay = '1')
myeloid_samples = SampleAnalysis.objects.filter(panel = myeloid_panel_obj)

# loop through samples and pull out summary statement plus metadata
for s in myeloid_samples:
    output_list.append([
        str(s.id),
        str(s.get_checks()['current_status']),
        str(s.sample.sample_id),
        'myeloid',
        str(s.worksheet.ws_id),
        str(s.worksheet.run),
        create_myeloid_coverage_summary(s)['summary_0x'],
        create_myeloid_coverage_summary(s)['summary_270x'],
    ])


# repeat above for MPN panel
mpn_panel_obj = Panel.objects.get(panel_name = 'mpn')
mpn_samples = SampleAnalysis.objects.filter(panel = mpn_panel_obj)

for s in mpn_samples:
    output_list.append([
        str(s.id),
        str(s.get_checks()['current_status']),
        str(s.sample.sample_id),
        'mpn',
        str(s.worksheet.ws_id),
        str(s.worksheet.run),
        create_myeloid_coverage_summary(s)['summary_0x'],
        create_myeloid_coverage_summary(s)['summary_270x'],
    ])


# repeat above for CLL panel
cll_panel_obj = Panel.objects.get(panel_name = 'cll')
cll_samples = SampleAnalysis.objects.filter(panel = cll_panel_obj)

for s in cll_samples:
    output_list.append([
        str(s.id),
        str(s.get_checks()['current_status']),
        str(s.sample.sample_id),
        'cll',
        str(s.worksheet.ws_id),
        str(s.worksheet.run),
        create_myeloid_coverage_summary(s)['summary_0x'],
        create_myeloid_coverage_summary(s)['summary_270x'],
    ])


# output data from all three panels to screen (redirect to output file in shell)
for line in output_list:
    print('\t'.join(line))
