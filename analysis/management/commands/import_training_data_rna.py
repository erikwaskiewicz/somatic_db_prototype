
from django.core.management.base import BaseCommand, CommandError
from analysis.models import *
import random
import csv

class Command(BaseCommand):
    help = "Import some test data"

    def handle(self, *args, **options):

        # TODO transactions.atomic????
        #input_file = '/home/erik/projects/somatic_db/analysis/test_data/ref_sample_colorectal.csv'
        input_run_id = 'training-data-RNA'
        input_ws = 'RNA-training-1'
        input_sample = 'RNA-sample-1'
        input_sample_type = 'RNA'
        input_panel = 'NTRK'

        # get panel object
        panel_obj = Panel.objects.get(panel_name=input_panel)

        # make run
        new_run, created = Run.objects.get_or_create(run_id=input_run_id)
        new_run.save()

        # make ws
        new_ws = Worksheet(
            ws_id=input_ws,
            run=new_run,
            assay='TSO500',
        )
        new_ws.save()

        # make samples
        total_reads = random.choice([9000001, 8000000])
        try:
            new_sample = Sample.objects.get(
                sample_id=input_sample,
                sample_type=input_sample_type,
            )
        except:
            new_sample = Sample(
                sample_id=input_sample,
                sample_type=input_sample_type,
                total_reads=total_reads,
                total_reads_ntc=1,
                percent_reads_ntc=int((1 / total_reads)*100),
            )
        new_sample.save()

        # make sample analysis and checks
        new_sample_analysis = SampleAnalysis(
            worksheet=new_ws,
            sample=new_sample,
            panel=panel_obj,
        )
        new_sample_analysis.save()
    
        new_check = Check(
            analysis=new_sample_analysis,
            stage='IGV',
            status='P',
        )
        new_check.save()

        # make fusions
        new_fusion, created = Fusion.objects.get_or_create(
            fusion_genes = 'NTRK1-TPM3',
            left_breakpoint = '1:156000000',
            right_breakpoint = '1:154000000',
        )
        new_fusion.save()

        new_fusion_instance = FusionAnalysis(
            sample=new_sample_analysis,
            fusion_genes=new_fusion,
            fusion_supporting_reads=30,
            split_reads=10,
            spanning_reads=20,
            fusion_caller='Manta',
            fusion_score='100',
            in_ntc=False,
        )
        new_fusion_instance.save()

        new_fusion_analysis = FusionPanelAnalysis(
            sample_analysis = new_sample_analysis,
            fusion_instance = new_fusion_instance,
        )
        new_fusion_analysis.save()

        new_fusion_check = FusionCheck(
            fusion_analysis = new_fusion_analysis,
            check_object = new_check,
        )
        new_fusion_check.save()
