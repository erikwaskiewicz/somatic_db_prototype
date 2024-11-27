from django.test import TestCase
from germline_classification.models import *

class TestClassification(TestCase):
    """
    Tests for the Classification model
    """

    def test_classify_acgs_2024(self):
        self.assertEqual(Classification.classify_acgs_2024(12), "pathogenic")
        self.assertEqual(Classification.classify_acgs_2024(8), "likely_pathogenic")
        self.assertEqual(Classification.classify_acgs_2024(5), "vus_hot")
        self.assertEqual(Classification.classify_acgs_2024(2), "vus_warm")
        self.assertEqual(Classification.classify_acgs_2024(0), "vus_cold")
        self.assertEqual(Classification.classify_acgs_2024(-4), "likely_benign")
        self.assertEqual(Classification.classify_acgs_2024(-8), "benign")