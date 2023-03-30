# Description:
# Set the checks for the poly list to complete, to be done after DB change, wont be needed in future as check will happen as we go along
# 
# Date: 30/12/2022
# Use: python manage.py shell < /home/ew/somatic_db/queries/fix_polys.py


from analysis.models import VariantToVariantList, VariantList
from django.contrib.auth.models import User
from datetime import datetime

user = User.objects.get(username='admin')
vars = VariantToVariantList.objects.all()

new_poly_list = VariantList.objects.get(name='build_37_polys')
print(new_poly_list)

for v in vars:
    #print(v)
    v.variant_list = new_poly_list
    v.save()
