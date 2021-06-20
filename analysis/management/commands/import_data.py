
from django.core.management.base import BaseCommand, CommandError
from analysis.models import *
import random

class Command(BaseCommand):
    help = "Import some test data"

    def handle(self, *args, **options):

        all_panels = Panel.objects.all()

        # make run
        run_id=f'210101_A123_{random.randrange(1,300)}_ABJHGFT4GHUJ6'
        new_run = Run(run_id=run_id)
        new_run.save()
        print(run_id)

        # make ws(s)
        for i in range(0, random.randrange(1,3)):
            ws = f'21-{random.randrange(10,900)}'
            new_ws = Worksheet(
                ws_id=ws,
                run=new_run,
                assay='TSO500',
            )
            new_ws.save()

            # make samples
            for s in range(0, random.randrange(1,10)):
                sample = f'21M{random.randrange(100,5000)}'
                sample_type = random.choice(['DNA', 'RNA'])
                # TODO should be get or create - the same sample might have been run before??
                new_sample = Sample(
                    sample_id=sample,
                    sample_type=sample_type,
                )
                new_sample.save()

                # make sample analysis and checks
                panel = random.choice(all_panels)

                new_sample_analysis = SampleAnalysis(
                    worksheet=new_ws,
                    sample=new_sample,
                    panel=panel,
                )
                new_sample_analysis.save()
            
                new_check = Check(
                    analysis=new_sample_analysis,
                    stage='IGV',
                    status='P',
                )
                new_check.save()


                # make variants and variant checks
                for v in range(0, random.randrange(1,15)):
                    hgvs_g = f'{random.randrange(1,23)}:{random.randrange(100,5000)}A>G'
                    # TODO should be get or create
                    new_var = Variant(
                        genomic_37 = hgvs_g,
                        genomic_38 = hgvs_g,
                        gene = random.choice(['EGFR', 'BRAF', 'KRAS']),
                        exon = '1 | 10',
                        transcript = 'NM12345.6',
                        hgvs_c = 'c.12345A>G',
                        hgvs_p = 'p.Arg123Pro',
                    )
                    new_var.save()

                    new_var_analysis = VariantAnalysis(
                        sample=new_sample_analysis,
                        variant=new_var,
                        vaf=random.randrange(1,100),
                        total_count=random.randrange(1,100),
                        alt_count=random.randrange(1,10),
                    )
                    new_var_analysis.save()

                    new_var_check = VariantCheck(
                        variant_analysis=new_var_analysis,
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
                            hgvs_c='c.123_789',
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
                            hgvs_c='c.12_34',
                            chr_start='7',
                            pos_start=1234,
                            chr_end='7',
                            pos_end=5678,
                            coverage_cutoff=random.choice([135, 270]),
                            percent_cosmic=1,
                        )
                        new_gap_obj.save()
                    print(g)


