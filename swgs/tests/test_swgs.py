from django.test import TestCase
from swgs.tests.test_data.example_inputs import *
from swgs.tests.test_data.expected_results import *
from swgs.utils import *

class TestVCFToDict(TestCase):
    """
    checks the functionality in utils.py to convert a VCF to a dictionary
    large expected results and example inputs in expected_results.py / example_inputs.py
    """

    def setUp(self):
        self.somatic_vcf = "swgs/tests/test_data/Test_somatic.vcf.gz"

    def test_read_in_vcf(self):
        header_lines, variants = read_in_vcf(self.somatic_vcf)
        self.assertEqual(header_lines, expected_header_lines)
        self.assertEqual(variants, expected_variants)

    def test_get_variant_keys(self):
        description_line = "#CHROM\tpos\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tTEST_GERMLINE\tTEST_SOMATIC\n"
        variant_keys = get_variant_keys(description_line)
        self.assertEqual(variant_keys, expected_variant_keys)

    def test_get_vep_fields_from_header(self):
        vep_info_fields = get_vep_fields_from_header(expected_header_lines)   
        self.assertEqual(vep_info_fields, expected_vep_info_fields)

    def test_convert_info_field_to_dict(self):
        info_dict = convert_info_field_to_dict(example_info_field, expected_vep_info_fields)
        self.assertEqual(info_dict, expected_info_dict)
        
    def test_convert_sample_information_to_dict(self):
        samples_info_dict = convert_sample_information_to_dict(example_format_and_sample_dict, example_format_and_sample_keys)
        self.assertEqual(samples_info_dict, expected_samples_info_dict)

    def test_create_variants_dictionary(self):
        variants_dictionary = create_variants_dictionary(expected_variant_keys, expected_variants, expected_vep_info_fields)
        self.assertEqual(variants_dictionary, expected_variants_dictionary)

    def test_vcf_to_variants_dictionary(self):
        variants_dictionary = vcf_to_variants_dictionary(self.somatic_vcf)
        self.assertEqual(variants_dictionary, expected_variants_dictionary)

    def tearDown(self):
        pass