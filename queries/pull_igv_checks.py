# Description:
# Pull out all individual variant IGV checks between two dates, date range hardcoded in script
# 
# Date: 11/10/2023 - SS
# Use: python manage.py shell < /home/ew/somatic_db/queries/pull_igv_checks.py (with somatic_variant_db env activated)
# Result is printed to screen, can be piped into sort | uniq -c to count occurrences

import datetime
from analysis.models import VariantInstance, SampleAnalysis, VariantPanelAnalysis
from django.contrib.humanize.templatetags.humanize import ordinal

#set date range
start_date = datetime.date(2023, 9, 21)
end_date = datetime.date(2023, 10, 11)

#Get all sample analyses
samples = SampleAnalysis.objects.all()

#Loop over samples
for s in samples:

	#Get all IGV checks
	checks = s.get_checks()['all_checks']
	
	#Use date of first check therefore will be after go live
	#if the check is between the dates, get it
	if checks[0].signoff_time != None:
	
		within_timeframe = start_date <= checks[0].signoff_time.date() <= end_date
		if within_timeframe:
	
			#Now we know the checks for the sample analysis were in the date range, get variant panel analysis for that sample analysis
			variant_analyses = VariantPanelAnalysis.objects.filter(sample_analysis = s)
				
			#Get checks
			for v in variant_analyses:
			
				variant_checks = v.get_all_checks()
				
				#Get decision for each check
				for result in variant_checks:
				
					#If decision not Geniune or pending, print out
					if result.get_decision_display() != "Geniune" and result.get_decision_display() != "Pending":
					
						print(result.variant_analysis.variant_instance.variant.variant,result.get_decision_display()) 
