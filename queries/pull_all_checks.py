# Description:
# Pull out all individual checks between two dates, date range hardcoded in script
# 
# Date: 27/09/2022 - EW
# Use: python manage.py shell < /home/ew/somatic_db/queries/pull_out_checks.py (with somatic_variant_db env activated)


import datetime
from analysis.models import SampleAnalysis
from django.contrib.humanize.templatetags.humanize import ordinal


# set date range
start_date = datetime.date(2021, 1, 1)
end_date = datetime.date(2024, 3, 8)

# headers and list to save output
out_list = [['Sample', 'Worksheet', 'Assay', 'Run', 'Date', 'Check #', 'Number of checks', 'Check result', 'User', 'Database link']]

# get all sample analyses and loop through
samples = SampleAnalysis.objects.all()
for s in samples:

    num_checks = str(len(s.get_checks()['all_checks']))

    # get all checks for each sample analysis
    for n, check in enumerate(s.get_checks()['all_checks']):

        # marker whether to include in output, will be overwritten if check is to be filtered
        include = True

        # pull out user, exclude from output if unassigned
        try:
            username = check.user.username
        except:
            username = 'Unassigned'
            include = False

        # pull out signoff date, remove if empty or outside of range specified above
        signoff = check.signoff_time
        if signoff == None:
            include = False
        else:
            within_timeframe = start_date <= signoff.date() <= end_date
            if within_timeframe:
                signoff = signoff.strftime('%Y-%m-%d')
            else:
                include = False

        # remove any incomplete checks
        status = check.get_status_display()
        if status == 'Pending':
            include = False

        # only add the correct checks to the output
        if include == True:
            count = f'{ordinal(n+1)} check'
            link = f'http://10.59.210.247:8000/analysis/{s.id}#report'
            out_list.append([
                s.sample.sample_id,
                s.worksheet.ws_id,
                s.worksheet.assay,
                s.worksheet.run.run_id,
                signoff,
                count,
                num_checks,
                status,
                username,
                link,
            ])

# pritn to screen (can redirect to file in shell)
for line in out_list:
    print(','.join(line))
