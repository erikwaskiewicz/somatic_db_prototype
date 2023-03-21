
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from analysis.models import *

import os
import csv
import json
import yaml
import pybedtools
import numpy as np
from datetime import datetime


class Command(BaseCommand):
    help = "Import a DNA run"

    def add_arguments(self, parser):
        parser.add_argument('--run', nargs=1, type=str, required=True, help='Run ID')
        parser.add_argument('--worksheet', nargs=1, type=str, required=True, help='Worksheet')
        parser.add_argument('--assay', nargs=1, type=str, required=True, help='Assay')
        parser.add_argument('--sample', nargs=1, type=str, required=True, help='Sample ID')
        parser.add_argument('--panel', nargs=1, type=str, required=True, help='Name of virtual panel applied')
        parser.add_argument('--genome', nargs=1, type=str, required=True, help='Reference genome as GRCh37 or GRCh38')
        parser.add_argument('--debug', nargs=1, type=str, required=True, help='Show detailed logging')

        # SNV/ indel only
        parser.add_argument('--snvs', nargs=1, type=str, required=False, help='Path to SNVs CSV file')
        parser.add_argument('--snv_coverage', nargs=1, type=str, required=False, help='Path to coverage JSON file')

        # fusion only
        parser.add_argument('--fusions', nargs=1, type=str, required=False, help='Path to fusions CSV file')
        parser.add_argument('--fusion_coverage', nargs=1, type=str, required=False, help='sample and NTC coverage, seperated by commas')



    @transaction.atomic
    def handle(self, *args, **options):
        """
        Run sample upload script
        """

        # ---------------------------------------------------------------------------------------------------------
        # Setup
        # ---------------------------------------------------------------------------------------------------------

        # extract variables from argparse
        run_id = options['run'][0]
        ws = options['worksheet'][0]
        sample = options['sample'][0]
        debug_input = options['debug'][0]
        # convert string to boolean
        debug = bool(debug_input == 'True')

        # check assay is in list and use to extract variables
        assay = options['assay'][0]
        assay_choices = {
            'TSO500_DNA': {
                'model_key': '1',
                'sample_type': 'DNA'
            },
            'TSO500_RNA': {
                'model_key': '2',
                'sample_type': 'RNA'
            },
            'TSO500_ctDNA': {
                'model_key': '3',
                'sample_type': 'ctDNA'
            },
        }
        if assay not in assay_choices.keys():
            print(f'ERROR\t{datetime.now()}\timport.py\tUnknown assay - {assay}')
            raise IOError(f'ERROR\tUnknown assay - {assay}')

        # check genome build is in list # TODO pnel folder needs to be more specific
        genome = options['genome'][0]
        if genome == 'GRCh38':
            genome_build = 38
            panel_folder = settings.ROI_PATH_B38
        elif genome == 'GRCh37':
            genome_build = 37
            panel_folder = settings.ROI_PATH_DNA
        else:
            raise IOError(f'Genome build {genome} is neither GRCh37 or GRCh38')


        # ---------------------------------------------------------------------------------------------------------
        # Sample level objects
        # ---------------------------------------------------------------------------------------------------------

        # get panel object TODO - add error if doesnt exist
        panel = options['panel'][0]
        panel_obj = Panel.objects.get(panel_name=panel, assay=assay_choices[assay]['model_key'], live=True) # TODO need to map these to assay choices in model

        # make run
        new_run, created = Run.objects.get_or_create(run_id=run_id)

        # make ws
        new_ws = Worksheet(
            ws_id=ws,
            run=new_run,
            assay=assay,
        )
        new_ws.save()

        # make samples
        new_sample, created = Sample.objects.get_or_create(
            sample_id=sample,
            sample_type=assay_choices[assay]['sample_type'],
        )

        # make sample analysis and checks
        new_sample_analysis = SampleAnalysis(
            worksheet=new_ws,
            sample=new_sample,
            panel=panel_obj,
            genome_build=genome_build,
        )
        # add num reads if in panel settings
        if panel_obj.show_fusion_coverage:
            total_cov, ntc_cov = options['fusion_coverage'][0].split(',')
            new_sample_analysis.total_reads = total_cov
            new_sample_analysis.total_reads_ntc = ntc_cov
            # TODO - round better and handle zero division error
            percent_reads_ntc=int((int(ntc_cov) / int(total_cov))*100)
            new_sample_analysis.percent_reads_ntc = percent_reads_ntc

        new_sample_analysis.save()

        new_check = Check(
            analysis=new_sample_analysis,
            stage='IGV',
            status='P',
        )
        new_check.save()


        # ---------------------------------------------------------------------------------------------------------
        # SNVs and indels
        # ---------------------------------------------------------------------------------------------------------
        if panel_obj.show_snvs:

            snvs_file = options['snvs'][0]
            coverage_file = options['snv_coverage'][0]

            # check that inputs are valid
            if not os.path.isfile(snvs_file):
                raise IOError(f'{snvs_file} file does not exist')
            if not os.path.isfile(coverage_file):
                raise IOError(f'{coverage_file} file does not exist')

            # TODO - attach file to models???
            panel_bed_file = f'{panel_folder}/{panel}.bed' 
            if not os.path.isfile(panel_bed_file):
                raise IOError(f'{panel_bed_file} file does not exist')

            # open bed file object
            panel_bed = pybedtools.BedTool(panel_bed_file)




            # counter for logging
            snv_counter = 0
            print(f'INFO\t{datetime.now()}\timport.py\tUploading SNVs...')

            # make variants and variant checks
            vaf_threshold = panel_obj.vaf_cutoff

            with open(snvs_file) as f:
                reader = csv.DictReader(f, delimiter='\t')

                for v in reader:

                    # format pos, chr, ref etc as genomic coords
                    genomic_coords = f"{v['chr'].strip('chr')}:{v['pos']}{v['ref']}>{v['alt']}"

                    # determine whether or not VAF is above threshold
                    vaf = float(v['vaf']) * 100
                    above_vaf_threshold = (vaf >= vaf_threshold)

                    # variant object is created for all variants across whole panel
                    new_var, created = Variant.objects.get_or_create(
                        variant = genomic_coords,
                        genome_build = genome_build,
                    )

                    ## check if variant is within the virtual panel
                    # format variant pos as a line of bed file 
                    variant_as_bed=f"{v['chr'].strip('chr')}\t{int(v['pos']) -1}\t{v['pos']}"
                    variant_bed_region = pybedtools.BedTool(variant_as_bed, from_string=True)

                    # boolean if variant overlaps with panel
                    overlaps_panel = len(panel_bed.intersect(variant_bed_region)) > 0

                    # if both booleans true, enter loop
                    if overlaps_panel and above_vaf_threshold:
                        if debug:
                            print(f'DEBUG\t{datetime.now()}\timport.py\tAdding variant: {v}')
                    
                        # if gnomad frequency not there, make it None
                        if 'gnomad_popmax_AF' not in v:
                            v['gnomad_popmax_AF'] = None

                        # make new instance of variant
                        new_var_instance = VariantInstance(
                            sample = new_sample,
                            variant = new_var,
                            gene = v['gene'],
                            exon = v['exon'],
                            hgvs_c = v['hgvs_c'],
                            hgvs_p = v['hgvs_p'],
                            total_count = v['depth'],
                            alt_count = v['alt_reads'],
                            in_ntc = v['in_ntc'],
                            gnomad_popmax = v['gnomad_popmax_AF'],
                        )
                        
                        # add NTC read counts if the variant is seen in the NTC. For new database had to convert string to boolean #TODO - do in reverse?
                        if v['in_ntc'] == "False":
                            v['in_ntc'] = False
                            
                        if v['in_ntc']:
                            new_var_instance.total_count_ntc = v['ntc_depth']
                            new_var_instance.alt_count_ntc = v['ntc_alt_reads']
                        
                        new_var_instance.save()

                        # put on panel
                        new_var_panel_analysis = VariantPanelAnalysis(
                            sample_analysis = new_sample_analysis,
                            variant_instance = new_var_instance,
                        )
                        new_var_panel_analysis.save()

                        # add check
                        new_var_check = VariantCheck(
                            variant_analysis=new_var_panel_analysis,
                            check_object=new_check,
                        )
                        new_var_check.save()

                        # logging
                        snv_counter += 1
                        if debug:
                            print(f'DEBUG\t{datetime.now()}\timport.py\tVariant added successfully')

            # logging
            print(f'INFO\t{datetime.now()}\timport.py\tFinished uploading successfully - added {snv_counter} variant(s)')
            print(f'INFO\t{datetime.now()}\timport.py\tUploading coverage data...')


            # ---------------------------------------------------------------------------------------------------------
            # Coverage
            # ---------------------------------------------------------------------------------------------------------

            # make coverage data - coverage json is already filtered for panel
            with open(coverage_file, 'r') as f:
                coverage_dict = json.load(f)

            # get required coverage values from panel
            coverage_thresholds = panel_obj.depth_cutoffs.split('|')

            for g, values in coverage_dict.items():
                # get gene object
                gene, created = Gene.objects.get_or_create(gene=g)

                # get the coverage values, if they're missing default to none
                percent_135x = values.get('percent_135', None)
                percent_270x = values.get('percent_270', None)
                percent_1000x = values.get('percent_1000', None)

                # save to db
                new_gene_coverage_obj = GeneCoverageAnalysis(
                    sample=new_sample_analysis,
                    gene=gene,
                    av_coverage=values['average_depth'],
                    percent_135x=percent_135x,
                    percent_270x=percent_270x,
                    percent_1000x=percent_1000x,
                    av_ntc_coverage=values['average_ntc'],
                    percent_ntc=values['percent_ntc'],
                )
                new_gene_coverage_obj.save()


                # hotspot regions - TODO different coverage values - not sure this works without being a dict
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
            
                # gaps 135x
                if '135' in coverage_thresholds:
                    for gap in values['gaps_135']:
                        
                        #if there is no cosmic percent or count present, make this 0 (so adding two numbers to the list)
                        if len(gap) < 6:
                            gap.append(None)
                            gap.append(None)
                            
                        #if cosmic percent is NaN (because no cosmic annotations for that referral), make it 0 (html displays NA in these cases)
                        #if np.isnan(gap[6]):
                        #    gap[6] = None
                        
                        new_gap_obj = GapsAnalysis(
                            gene=new_gene_coverage_obj,
                            hgvs_c=gap[3],
                            chr_start=gap[0],
                            pos_start=gap[1],
                            chr_end=gap[0],
                            pos_end=gap[2],
                            coverage_cutoff=135,
                            percent_cosmic=gap[6],
                        )
                        new_gap_obj.save()

                # gaps 270x
                if '270' in coverage_thresholds:
                    for gap in values['gaps_270']:
                        
                        #if there is no cosmic percent present, make this 0 (so adding two numbers to the list)
                        if len(gap) < 6:
                            gap.append(None)
                            gap.append(None)
                    
                        #if cosmic percent is NaN (because no cosmic annotations for that referral), make it 0 (html displays NA in these cases)
                        #if np.isnan(gap[6]):
                        #    gap[6] = None
                            
                        new_gap_obj = GapsAnalysis(
                            gene=new_gene_coverage_obj,
                            hgvs_c=gap[3],
                            chr_start=gap[0],
                            pos_start=gap[1],
                            chr_end=gap[0],
                            pos_end=gap[2],
                            coverage_cutoff=270,
                            percent_cosmic=gap[6],
                        )
                        new_gap_obj.save()

                # gaps 1000x
                if '1000' in coverage_thresholds:
                    for gap in values['gaps_1000']:
                        
                        #if there is no cosmic percent present, make this 0 (so adding two numbers to the list)
                        if len(gap) < 6:
                            gap.append(None)
                            gap.append(None)
                    
                        #if cosmic percent is NaN (because no cosmic annotations for that referral), make it 0 (html displays NA in these cases)
                        #if np.isnan(gap[6]):
                        #    gap[6] = None
                            
                        new_gap_obj = GapsAnalysis(
                            gene=new_gene_coverage_obj,
                            hgvs_c=gap[3],
                            chr_start=gap[0],
                            pos_start=gap[1],
                            chr_end=gap[0],
                            pos_end=gap[2],
                            coverage_cutoff=1000,
                            percent_cosmic=gap[6],
                        )
                        new_gap_obj.save()

            # logging
            print(f'INFO\t{datetime.now()}\timport.py\tFinished uploading coverage data')


        # ---------------------------------------------------------------------------------------------------------
        # fusions
        # ---------------------------------------------------------------------------------------------------------

        if panel_obj.show_fusions:
            fusions_file = options['fusions'][0]
            panels_file = settings.ROI_PATH_RNA # TODO - from panel?

            # check that inputs are valid
            if not os.path.isfile(fusions_file):
                raise IOError(f'{fusions_file} file does not exist')
            if not os.path.isfile(panels_file):
                raise IOError(f'{panels_file} file does not exist')

            # load in virtual panel
            with open(panels_file) as f:
                referrals = yaml.load(f, Loader=yaml.FullLoader)
            virtual_panel = referrals[panel]

            # logging
            fusion_counter = 0
            print(f'INFO\t{datetime.now()}\timport.py\tUploading fusions...')

            # load in fusion calls
            with open(fusions_file) as f:

                # make dictionary of calls and loop through
                reader = csv.DictReader(f, delimiter=',')
                for f in reader:

                    # format fusion field and filter panel
                    in_panel = False
                    
                    # splice variants
                    if f['type'] == 'Splice':
                        # add exon number to gene name
                        fusion = f"{f['fusion']} {f['exons']}"

                        # check splicing gene list and set variable if matches
                        if 'splicing' in virtual_panel.keys():
                            if f['fusion'] in virtual_panel['splicing']:
                                in_panel = True

                    # gene fusions
                    elif f['type'] == 'Fusion':
                        # use pipeline output directly (will be GENE_A--GENE_B)
                        fusion = f['fusion']

                        # check fusion gene list and set variable if matches
                        for g in virtual_panel['fusions']:
                            if g in fusion:
                                in_panel = True

                    # add record for fusion (regardless of whether it's in the panel or not)
                    new_fusion, created = Fusion.objects.get_or_create(
                        fusion_genes = fusion,
                        left_breakpoint = f['left_breakpoint'],
                        right_breakpoint = f['right_breakpoint'],
                        genome_build = genome_build
                    )

                    # if the fusion was in the panel, make a fusion instance
                    if in_panel:
                        # logging
                        if debug:
                            print(f'DEBUG\t{datetime.now()}\timport.py\tAdding fusion: {f}')

                        #TODO change hard coded variables - they should be optional
                        new_fusion_instance = FusionAnalysis(
                            sample = new_sample_analysis,
                            fusion_genes = new_fusion,
                            fusion_supporting_reads = f['fusion_supporting_reads'],
                            ref_reads_1 = f['reference_reads_1'],
                            fusion_caller = f['type'],
                            in_ntc = f['in_ntc'],
                        )
                        # splice variants only have one reference value, fusions have two (one per gene)
                        if f['type'] == 'Fusion':
                            # reference reads 2 isnt always included if the fusion is intragenic
                            if f['reference_reads_2'] != 'NA':
                                new_fusion_instance.ref_reads_2 = f['reference_reads_2']
                            new_fusion_instance.fusion_score = f['fusion_score']
                            new_fusion_instance.split_reads = f['split_reads']
                            new_fusion_instance.spanning_reads = f['spanning_reads']
                        new_fusion_instance.save()

                        # set up virtual panel
                        new_fusion_analysis = FusionPanelAnalysis(
                            sample_analysis = new_sample_analysis,
                            fusion_instance = new_fusion_instance,
                        )
                        new_fusion_analysis.save()

                        # set up check object
                        new_fusion_check = FusionCheck(
                            fusion_analysis = new_fusion_analysis,
                            check_object = new_check,
                        )
                        new_fusion_check.save()

                        # logging
                        fusion_counter += 1
                        if debug:
                            print(f'DEBUG\t{datetime.now()}\timport.py\tFusion added successfully')

                # logging
                print(f'INFO\t{datetime.now()}\timport.py\tFinished uploading successfully - added {fusion_counter} fusions(s)')

        # close
        print(f'INFO\t{datetime.now()}\timport.py\tFinished import.py script successfully')
