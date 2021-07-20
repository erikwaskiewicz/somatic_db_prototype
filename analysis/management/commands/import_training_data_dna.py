
from django.core.management.base import BaseCommand, CommandError
from analysis.models import *
import random
import csv
import json


class Command(BaseCommand):
    help = "Import some test data"

    def handle(self, *args, **options):

        worksheet = '21-030'
        run_id = 'dna_training_run'

        # TODO transactions.atomic????


        input_dict = {
            'sample_1': {
                'variants_file': '/home/webapps/somatic_db_training_samples/21M06864-1/21M06864-1_Lung.tsv',
                'coverage_file': '/home/webapps/somatic_db_training_samples/21M06864-1/21M06864-1_Lung_coverage.json',
                'run_id': run_id,
                'ws': worksheet,
                'sample': '21M06864-1',
                'sample_type': 'DNA',
                'panel': 'Lung'
            },
            'sample_2': {
                'variants_file': '/home/webapps/somatic_db_training_samples/20M15539-2/20M15539-2_Melanoma.tsv',
                'coverage_file': '/home/webapps/somatic_db_training_samples/20M15539-2/20M15539-2_Melanoma_coverage.json',
                'run_id': run_id,
                'ws': worksheet,
                'sample': '20M15539-2',
                'sample_type': 'DNA',
                'panel': 'Melanoma'
            },
            'sample_3': {
                'variants_file': '/home/webapps/somatic_db_training_samples/20M14433/20M14433_Thyroid.tsv',
                'coverage_file': '/home/webapps/somatic_db_training_samples/20M14433/20M14433_Thyroid_coverage.json',
                'run_id': run_id,
                'ws': worksheet,
                'sample': '20M14433',
                'sample_type': 'DNA',
                'panel': 'Thyroid'
            },
        }



        for key, values in input_dict.items():

            input_file = values['variants_file']
            input_coverage_file = values['coverage_file']
            input_run_id = values['run_id']
            input_ws = values['ws']
            input_sample = values['sample']
            input_sample_type = values['sample_type']
            input_panel = values['panel']

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
            try:
                new_sample = Sample.objects.get(
                    sample_id=input_sample,
                    sample_type=input_sample_type,
                )
            except:
                new_sample = Sample(
                    sample_id=input_sample,
                    sample_type=input_sample_type,
                    total_reads=1,
                    total_reads_ntc=0,
                    percent_reads_ntc=0,
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


            # make variants and variant checks
            with open(input_file) as f:
                reader = csv.DictReader(f, delimiter='\t')
                for v in reader:
                    print(v)
                    genomic_coords = f"{v['chr'].strip('chr')}:{v['pos']}{v['ref']}>{v['alt']}"
                    vaf = int(float(v['vaf']) * 100)
                    print(vaf)
                    print(genomic_coords)

                    new_var, created = Variant.objects.get_or_create(
                        genomic_37 = genomic_coords,
                        genomic_38 = None,
                        gene = v['gene'],
                        exon = v['exon'],
                        transcript = '-',
                        hgvs_c = v['hgvs_c'],
                        hgvs_p = v['hgvs_p'],
                    )
                    new_var.save()

                    new_var_instance = VariantInstance(
                        sample=new_sample,
                        variant=new_var,
                        vaf=vaf,
                        total_count=v['depth'],
                        alt_count=v['alt_reads'],
                        in_ntc=v['in_ntc'],
                    )
                    new_var_instance.save()

                    # put on panel
                    new_var_panel_analysis = VariantPanelAnalysis(
                        sample_analysis = new_sample_analysis,
                        variant_instance = new_var_instance,
                    )
                    new_var_panel_analysis.save()

                    new_var_check = VariantCheck(
                        variant_analysis=new_var_panel_analysis,
                        check_object=new_check,
                    )
                    new_var_check.save()

            # make coverage data
            with open(input_coverage_file, 'r') as f:
                coverage_dict = json.load(f)


            for g, values in coverage_dict.items():
                #print(values)

                gene, created = Gene.objects.get_or_create(gene=g)

                new_gene_coverage_obj = GeneCoverageAnalysis(
                    sample=new_sample_analysis,
                    gene=gene,
                    av_coverage=values['average_depth'],
                    percent_270x=values['percent_270'],
                    percent_135x=values['percent_135'],
                    av_ntc_coverage=values['average_ntc'],
                    percent_ntc=values['percent_ntc'],
                )
                new_gene_coverage_obj.save()


                # hotspot regions
                for r in values['hotspot_regions']:
                    new_regions_obj = RegionCoverageAnalysis(
                        gene=new_gene_coverage_obj,
                        hgvs_c=r[3],
                        chr_start=r[0],
                        pos_start=r[1],
                        chr_end=r[0],
                        pos_end=r[2],
                        hotspot='H',
                        average_coverage=r[4],
                        percent_270x=r[5],
                        percent_135x=r[6],
                        ntc_coverage=r[7],
                        percent_ntc=r[8],
                    )
                    new_regions_obj.save()

                # genescreen regions
                for r in values['genescreen_regions']:
                    new_regions_obj = RegionCoverageAnalysis(
                        gene=new_gene_coverage_obj,
                        hgvs_c=r[3],
                        chr_start=r[0],
                        pos_start=r[1],
                        chr_end=r[0],
                        pos_end=r[2],
                        hotspot='G',
                        average_coverage=r[4],
                        percent_270x=r[5],
                        percent_135x=r[6],
                        ntc_coverage=r[7],
                        percent_ntc=r[8],
                    )
                    new_regions_obj.save()
            
                for gap in values['gaps_135']:
                    new_gap_obj = GapsAnalysis(
                        gene=new_gene_coverage_obj,
                        hgvs_c=gap[3],
                        chr_start=gap[0],
                        pos_start=gap[1],
                        chr_end=gap[0],
                        pos_end=gap[2],
                        coverage_cutoff=135,
                        percent_cosmic=gap[4],
                    )
                    new_gap_obj.save()


                for gap in values['gaps_270']:
                    new_gap_obj = GapsAnalysis(
                        gene=new_gene_coverage_obj,
                        hgvs_c=gap[3],
                        chr_start=gap[0],
                        pos_start=gap[1],
                        chr_end=gap[0],
                        pos_end=gap[2],
                        coverage_cutoff=270,
                        percent_cosmic=gap[4],
                    )
                    new_gap_obj.save()
                #print(g)
