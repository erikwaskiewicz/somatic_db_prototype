# Description:
# Get all variants on a current poly list
 
# Date: 11/01/2023
# Use: python manage.py shell < /home/ew/somatic_db/queries/get_polys.py


from analysis.models import VariantToVariantList, VariantList, VariantInstance
from django.contrib.auth.models import User
from datetime import datetime

out_list=[]

#Get all variant to variantlist objects for the polys
vars = VariantToVariantList.objects.filter(variant_list__name="TSO500_polys")

#Got through these and get the variant info, incl gene and HGVS from the Variant Instance
for v in vars:
	
	#Get variant
	variant = v.variant.genomic_37

	#Get VariantInstance to get other info, will first one as the gene and HGVS won't change
	variant_instances = VariantInstance.objects.filter(variant=v.variant)
	
	#Not all polys have a variant instance! 
	if len(variant_instances) != 0:
		variant_instance = variant_instances[0]

		#Gene
		gene = variant_instance.gene

		#HGVSc 
		HGVSc = variant_instance.hgvs_c

		#HGVSp
		HGVSp = variant_instance.hgvs_p

	else:
		gene=""
		HGVSc=""
		HGVSp=""

	out_list.append([
		variant,
		gene,
		HGVSc,
		HGVSp,
		])

# print to screen (can redirect to file in shell)
for line in out_list:
    print(','.join(line))

	
