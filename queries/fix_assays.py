# Description:
# Assay was previously set to TSO500, but should be either TSO500_DNA or TSO500_RNA, loop through and correct in all worksheets
# 
# Date: 30/03/2023 - EW
# Use: python manage.py shell < /home/ew/somatic_db/queries/fix_assays.py (with somatic_variant_db env activated)


import datetime
from analysis.models import SampleAnalysis
from django.contrib.humanize.templatetags.humanize import ordinal



# get all sample analyses and loop through
samples = SampleAnalysis.objects.all()
for s in samples:
    if s.worksheet.assay == 'TSO500':
        ws = s.worksheet
        ws.assay = s.panel.get_assay_display().replace(' ', '_')
        ws.save()
