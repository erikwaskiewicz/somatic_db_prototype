
from django.core.management.base import BaseCommand, CommandError
from analysis.models import *
import random
import csv

class Command(BaseCommand):
    help = "Import some test data"

    def handle(self, *args, **options):

        # TODO transactions.atomic????
        input_file = '/home/erik/projects/somatic_db/analysis/test_data/ref_sample_colorectal.csv'
        input_run_id = 'training'
        input_ws = 'training-set-1'
        input_sample = '21M00305-1'
        input_sample_type = 'DNA'
        input_panel = 'Colorectal'

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
        for g in ['BRAF', 'NRAS', 'EGFR']:
            gene, created = Gene.objects.get_or_create(gene=g)

            new_gene_coverage_obj = GeneCoverageAnalysis(
                sample=new_sample_analysis,
                gene=gene,
                av_coverage=200,
                percent_270x=99,
                percent_135x=100,
                av_ntc_coverage=1,
                percent_ntc=0,
            )
            new_gene_coverage_obj.save()

            for r in range(0, random.randrange(1,15)):
                new_regions_obj = RegionCoverageAnalysis(
                    gene=new_gene_coverage_obj,
                    hgvs_c=f'{g} (NM_12345.6): c.123_789',
                    chr_start='7',
                    pos_start=1234,
                    chr_end='7',
                    pos_end=5678,
                    hotspot='H',
                    average_coverage=100,
                    percent_270x=99,
                    percent_135x=100,
                    ntc_coverage=0,
                    percent_ntc=0,
                )
                new_regions_obj.save()
            
            for gap in range(0, random.randrange(1,15)):
                new_gap_obj = GapsAnalysis(
                    gene=new_gene_coverage_obj,
                    hgvs_c=f'{g} (NM_12345.6): c.123_200',
                    chr_start='7',
                    pos_start=1234,
                    chr_end='7',
                    pos_end=5678,
                    coverage_cutoff=random.choice([135, 270]),
                    percent_cosmic=1,
                )
                new_gap_obj.save()
            #print(g)
