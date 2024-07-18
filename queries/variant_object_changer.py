## Description
# Change variant object applied to an variant instance

from analysis.models import VariantInstance, Variant, SampleAnalysis

section = VariantInstance.objects.filter(sample="23M91076",pk = 38859)
for s in section:
	entry = s.variant
	print(entry.pk)
	entry.pk = 198752
	entry.save()

	



"""
for s in section:
	if s.variant.variant == "7:116411774ACAAGCTCTTTCTTTCTC>A":
		print(s.pk)
		print(s.variant)
		print(s.variant.pk)
		print(type(s.variant.pk))
		s.variant.pk = 198752
		s.variant.variant = "7:116411875_116411891delCAAGCTCTTTCTTTCTC"
		s.save()
		print(s.variant.variant)
		print(s.gene)
		s.save()
"""
