# Use: python manage.py shell < /home/ew/somatic_db/queries/no_checks.py (with somatic_variant_db env activated

from analysis.models import SampleAnalysis

samples = SampleAnalysis.objects.filter(worksheet__ws_id='22-2786')

outlist = []
# Get sample with no checks

for s in samples:
	print(s.sample.sample_id)
	num_checks = str(len(s.get_checks()['all_checks']))
	print([s.sample.sample_id, num_checks])
	
	for n, check in enumerate(s.get_checks()['all_checks']):

		outlist.append([s.sample.sample_id, num_checks])
	
		

		
