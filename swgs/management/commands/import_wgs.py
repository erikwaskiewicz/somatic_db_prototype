import json

from django.core.management.base import BaseCommand
from django.db import transaction

from swgs.models import *

test_variant_json = "/home/na282549/code/somatic_db/test_vcf_to_json.json"
test_qc_json = "/home/na282549/code/somatic_db/Test_overall_qc.json"

class Command(BaseCommand):

    def handle(self, *args, **options):

        # set up test PatientAnalysis object to link to variants
        # Patient
        # Tumour Sample
        # Germline Sample
        # Indivation
        # Run
        # QCSomaticVAFDistribution
        # QCTumourInNormalContamination
        # QCGermlineCNVQuality
        # QCLowQualityTumourSample
        # QCNTCContamination (germline and tumour)

        # PatientAnalysis
        
        # get or create a patient object from the NHS number
        #TODO handle all these imports properly, for now we're doing dummy data
        patient_obj, created = Patient.objects.get_or_create(nhs_number="TEST123")

        # get or create the tumour sample
        tumour_sample_obj, created = Sample.objects.get_or_create(sample_id="23M19543")

        # get or create the germline sample if it's being used
        # TODO handle tumour only
        germline_sample_obj, created = Sample.objects.get_or_create(sample_id="23M19542")

        # get or create the indication
        indication_obj, created = Indication.objects.get_or_create(indication="Development", indication_pretty_print="development")

        # get or create the run
        run_obj, created = Run.objects.get_or_create(run="231103_A01771_0322_AHMHMWDRX3", worklist="CELL_LINES_TEST")

        # load in the qc data from the json file
        with open(test_qc_json, "r") as f:
            overall_qc_dict = json.load(f)
        
        print(overall_qc_dict)





        
        # load in json
        with open(test_json) as f:
            test_dict = json.load(f)

        print(test_dict)