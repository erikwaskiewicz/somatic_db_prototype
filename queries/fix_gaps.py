# Description:
# Gaps were missing a colon in early version of new pipeline, loop through them all and add it in
# 
# Date: 7/2/2024
# Use: python manage.py shell < /home/ew/somatic_db/queries/fix_gaps.py


from analysis.models import GapsAnalysis

all_gaps = GapsAnalysis.objects.all()

for gap in all_gaps:
    if ')c' in gap.hgvs_c:
        new_gap = gap.hgvs_c.replace(')c', '):c')
        print(gap.hgvs_c, new_gap)
        gap.hgvs_c = new_gap
        gap.save()        
