# Description:
# Pull out all individual checks for Natalia Ristic
# Panel, variants, date, 1/2/3 check?

# Date: 16/02/24 - NT
# Use: python manage.py shell < /home/ew/somatic_db/queries/nr_cases.py (with somatic_variant_db env activated)


from analysis.models import SampleAnalysis, VariantCheck
from django.contrib.humanize.templatetags.humanize import ordinal
from django.contrib.auth.models import User
import pandas as pd
checklist = [['Sample', 'Panel', 'Signoff_time', 'Check', 'Variant']]

#user = User.objects.filter(username='Natalia.Ristic@wales.nhs.uk')
data = VariantCheck.objects.all()

for d in data:

	if 'Natalia.Ristic@wales.nhs.uk' in str(d.check_object.user):

		checklist.append([
			d.check_object.analysis.sample.sample_id,
			d.check_object.analysis.panel.panel_name,
			d.check_object.signoff_time,
			d.check_object.stage,
			d.variant_analysis.variant_instance.variant.variant
		])	

df = pd.DataFrame(checklist, columns=['Sample', 'Panel', 'Signoff_time', 'Check', 'Variant'])

df.to_csv('NR_checks.csv')

