# Description:
# Set the checks for the poly list to complete, to be done after DB change, wont be needed in future as check will happen as we go along
# 
# Date: 30/12/2022
# Use: python manage.py shell < /home/ew/somatic_db/queries/fix_polys.py


from analysis.models import VariantToVariantList
from django.contrib.auth.models import User
from datetime import datetime

user = User.objects.get(username='admin')
vars = VariantToVariantList.objects.all()

time_now = datetime.now()

for v in vars:
    v.upload_user = user
    v.upload_time = time_now
    v.upload_comment = 'Auto-filled from previous poly list - EW 30/12/2022'
    v.check_user = user
    v.check_time = time_now
    v.check_comment = 'Auto-filled from previous poly list - EW 30/12/2022'
    v.save()
