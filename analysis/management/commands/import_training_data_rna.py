
from django.core.management.base import BaseCommand, CommandError
from analysis.models import *
import random
import csv

class Command(BaseCommand):
    help = "Import some test data"

    def handle(self, *args, **options):

        input_run_id = 'rna_training_run'
        input_ws = '21-115'

        input_dict = {
            'sample_1': {
                'sample': 'sample1',
                'sample_type': 'RNA',
                'panel': 'Lung',
                'total_reads': '28212809',
                'ntc_reads': '0',
                'splice': [
                    
                    ['MET', 'chr7:116312631', 'chr7:116315856', '11', '4714'],
                    ['MET', 'chr7:116411708', 'chr7:116414934', '2591', '641'],
                ],  # name, left, right, splice_reads, ref_reads
                'fusions': []
            },
            'sample_2': {
                'sample': 'sample2',
                'sample_type': 'RNA',
                'panel': 'Lung',
                'total_reads': '24541772',
                'ntc_reads': '0',
                'splice': [
                    ['EGFR', 'chr7:55087058', 'chr7:55223522', '21', '0'],
                ],
                'fusions': []
            },
            'sample_3': {
                'sample': 'sample3',
                'sample_type': 'RNA',
                'panel': 'Lung',
                'total_reads': '27729083',
                'ntc_reads': '0',
                'splice': [],
                'fusions': [
                    ['EML4-ALK', 'chr2:42522654', 'chr2:29446394', '126', '797', '106'],
                ],  # name, left, right, fusion_reads, ref_reads_1, ref_reads_2
            },
        }

        for key, values in input_dict.items():

            input_sample = values['sample']
            input_sample_type = values['sample_type']
            input_panel = values['panel']


            # TODO transactions.atomic????


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
            total_reads = values['total_reads']
            ntc_reads = values['ntc_reads']
            percent_reads_ntc=int((int(ntc_reads) / int(total_reads))*100)

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
                    total_reads_ntc=ntc_reads,
                    percent_reads_ntc=percent_reads_ntc,
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


            for f in values['fusions']:
                # make fusions
                new_fusion, created = Fusion.objects.get_or_create(
                    fusion_genes = f[0],
                    left_breakpoint = f[1],
                    right_breakpoint = f[2],
                )
                new_fusion.save()

                new_fusion_instance = FusionAnalysis(
                    sample=new_sample_analysis,
                    fusion_genes=new_fusion,
                    fusion_supporting_reads=f[3],
                    split_reads=1,
                    spanning_reads=1,
                    fusion_caller='Manta',
                    fusion_score='1',
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


            for f in values['splice']:
                # make fusions
                new_fusion, created = Fusion.objects.get_or_create(
                    fusion_genes = f[0],
                    left_breakpoint = f[1],
                    right_breakpoint = f[2],
                )
                new_fusion.save()

                new_fusion_instance = FusionAnalysis(
                    sample=new_sample_analysis,
                    fusion_genes=new_fusion,
                    fusion_supporting_reads=f[3],
                    split_reads=1,
                    spanning_reads=1,
                    fusion_caller='Manta',
                    fusion_score='1',
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

