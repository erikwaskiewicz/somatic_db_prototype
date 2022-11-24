from .models import *
from .forms import NewVariantForm, SubmitForm, VariantCommentForm, FusionCommentForm

from django.utils import timezone
from django.db import transaction



def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources 
    taken straight from https://xhtml2pdf.readthedocs.io/en/latest/usage.html#using-xhtml2pdf-in-django
    """
    result = finders.find(uri)
    if result:
            if not isinstance(result, (list, tuple)):
                    result = [result]
            result = list(os.path.realpath(path) for path in result)
            path=result[0]
    else:
            sUrl = settings.STATIC_URL        # Typically /static/
            sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
            mUrl = settings.MEDIA_URL         # Typically /media/
            mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

            if uri.startswith(mUrl):
                    path = os.path.join(mRoot, uri.replace(mUrl, ""))
            elif uri.startswith(sUrl):
                    path = os.path.join(sRoot, uri.replace(sUrl, ""))
            else:
                    return uri

    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                    'media URI must start with %s or %s' % (sUrl, mUrl)
            )
    return path

    
def get_samples(samples):
    """
    """
    # adds a record for each panel analysis - i.e. if a sample has two panels
    # it will have two records
    sample_dict = {}
    for s in samples:
        sample_id = s.sample.sample_id

        # if there haven't been any panels for the sample yet, add new sample to dict
        if sample_id not in sample_dict.keys():

            sample_dict[sample_id] = {
                'sample_id': sample_id,
                'dna_rna': s.sample.sample_type,
                'panels': [{
                    'analysis_id': s.pk,
                    'panel': s.panel.panel_name,
                    'checks': s.get_checks(),
                }]
            }

        # if there are already panels for sample, add new panel to sample record
        else:
            sample_dict[sample_id]['panels'].append({
                    'analysis_id': s.pk,
                    'panel': s.panel.panel_name,
                    'checks': s.get_checks(),
                }
            )

    return sample_dict


@transaction.atomic
def unassign_check(sample_analysis_obj):
    """

    """
    # get latest check  
    latest_check = sample_analysis_obj.get_checks()['current_check_object']

    # reset check
    latest_check.user = None
    latest_check.coverage_ntc_check = False
    latest_check.coverage_comment = ''
    latest_check.coverage_comment_updated = None
    latest_check.patient_info_check = False
    latest_check.overall_comment = ''
    latest_check.overall_comment_updated = None
    latest_check.signoff_time = None
    latest_check.save()
    
    # get dna variant checks and reset
    variant_checks = VariantCheck.objects.filter(check_object=latest_check)
    for c in variant_checks:
        c.decision = '-'
        c.comment = ''
        c.comment_updated = None
        c.save()

    # get rna variant checks and reset
    fusion_checks = FusionCheck.objects.filter(check_object=latest_check)
    for c in fusion_checks:
        c.decision = '-'
        c.comment = ''
        c.comment_updated = None
        c.save()

    return True


@transaction.atomic
def signoff_check(user, current_step_obj, sample_obj, status='C'):
    """

    """
    # get all variant checks for the sample
    if sample_obj.sample.sample_type == 'DNA':
        variant_checks = VariantCheck.objects.filter(check_object=current_step_obj)
    elif sample_obj.sample.sample_type == 'RNA':
        variant_checks = FusionCheck.objects.filter(check_object=current_step_obj)

    # make sure that none of the variant checks are still pending
    # this trigers view to render the error on the page, skip this validation for failed samples
    if status != 'F':
        for v in variant_checks:
            if v.decision == '-':
                return False


    # signoff current check
    now = timezone.now()
    current_step_obj.user = user
    current_step_obj.signoff_time = now
    current_step_obj.status = status
    
    # save object
    current_step_obj.save()

    return True


def make_next_check(sample_obj, next_step):
    """

    """
    # add new check object
    new_check_obj = Check(
        analysis=sample_obj, 
        stage=next_step,
        status='P',
    )

    # save object
    new_check_obj.save()

    if sample_obj.sample.sample_type == 'DNA':
        # make check objects for all variants
        variant_objects = VariantPanelAnalysis.objects.filter(sample_analysis=sample_obj)
        for v in variant_objects:
            new_variant_check = VariantCheck(
                variant_analysis = v,
                check_object = new_check_obj,
            )
            new_variant_check.save()

    elif sample_obj.sample.sample_type == 'RNA':
        # make check objects for all variants
        variant_objects = FusionPanelAnalysis.objects.filter(sample_analysis=sample_obj)
        for v in variant_objects:
            new_variant_check = FusionCheck(
                fusion_analysis = v,
                check_object = new_check_obj,
            )
            new_variant_check.save()

    return True


def get_sample_info(sample_obj):
    """

    """
    sample_data = {
        'sample_pk': sample_obj.pk,
        'dna_or_rna': sample_obj.sample.sample_type,
        'sample_id': sample_obj.sample.sample_id,
        'sample_name': sample_obj.sample.sample_name,
        'worksheet_id': sample_obj.worksheet.ws_id,
        'panel': sample_obj.panel.panel_name,
        'is_myeloid_referral': sample_obj.panel.show_myeloid_gaps_summary,
        'run_id': sample_obj.worksheet.run.run_id,
        'total_reads': sample_obj.total_reads,
        'total_reads_ntc': sample_obj.total_reads_ntc,
        'percent_reads_ntc': sample_obj.percent_reads_ntc,
        'checks': sample_obj.get_checks(),
    }
    return sample_data


def get_variant_info(sample_data, sample_obj):

    sample_variants = VariantPanelAnalysis.objects.filter(sample_analysis=sample_obj)

    variant_calls = []
    polys_list = []

    # TODO this bit isnt used yet - removed to speed up db
    # get list of other samples on the run
    #current_run_obj = sample_obj.worksheet.run
    #current_run_samples = SampleAnalysis.objects.filter(worksheet__run = current_run_obj)
    # remove dups
    #sample_objects = set([ s.sample for s in current_run_samples ])

    for sample_variant in sample_variants:

        variant_obj = sample_variant.variant_instance.variant

        # count how many times variant is present in other samples on the run
        #this_run_count = 0
        #for s in sample_objects:
        #    qs = VariantInstance.objects.filter(
        #        sample = s,
        #        variant = variant_obj,
        #    )
        #    if qs:
        #        this_run_count += 1

        # get whether the variant falls within a poly/ known list
        # TODO - will have to handle multiple poly/ known lists in future
        previous_classifications = []
        for l in VariantToVariantList.objects.filter(variant=variant_obj):
            if l.variant_list.name == 'TSO500_known':
                previous_classifications.append(l.classification)
            elif l.variant_list.name == 'TSO500_polys':
                previous_classifications.append('Poly')

        # get checks for each variant
        variant_checks = VariantCheck.objects.filter(variant_analysis=sample_variant).order_by('pk')
        variant_checks_list = [ v.get_decision_display() for v in variant_checks ]
        latest_check = variant_checks.latest('pk')

        # do the last two checks agree?
        last_two_checks_agree = True
        if len(variant_checks_list) > 1:

            last2 = variant_checks_list[-2:]
            # skip check if not analysed
            if last2[1] != 'Not analysed':
                if last2[0] != last2[1]:
                    last_two_checks_agree = False

        # set decision if falls in poly list, otherwise the finilise sample validation will fail
        if 'Poly' in previous_classifications:
            latest_check.decision ='P'
            latest_check.save()
        var_comment_form = VariantCommentForm(pk=latest_check.pk, comment=latest_check.comment)

        # get list of comments for variant
        variant_comments_list = []
        for v in variant_checks:
            if v.comment:
                variant_comments_list.append(
                    { 'comment': v.comment, 'user': v.check_object.user, 'updated': v.comment_updated, }
                )

        #Create a variant calls dictionary to pass to analysis-snvs.html
        variant_calls_dict = {
            'pk': sample_variant.pk,
            'variant_instance_pk': sample_variant.variant_instance.pk,
            'genomic': variant_obj.genomic_37,
            'igv_coords': variant_obj.genomic_37.strip('ACGT>'), #TODO what about dels?
            'gene': sample_variant.variant_instance.gene,
            'exon': sample_variant.variant_instance.exon,
            'hgvs_c': sample_variant.variant_instance.hgvs_c,
            'hgvs_p': sample_variant.variant_instance.hgvs_p,
            'this_run': {
                #'count': this_run_count, 
                #'total': len(sample_objects),
                'ntc': sample_variant.variant_instance.in_ntc,
                'alt_count_ntc': sample_variant.variant_instance.alt_count_ntc,
                'total_count_ntc': sample_variant.variant_instance.total_count_ntc,
                'vaf_ntc': sample_variant.variant_instance.vaf_ntc(),
            },   
            'previous_runs': {
                'known': ' | '.join(previous_classifications),
                'count': 'N/A', #previous_runs,
            },
            'vaf': {
                'vaf': sample_variant.variant_instance.vaf(),
                'total_count': sample_variant.variant_instance.total_count,
                'alt_count': sample_variant.variant_instance.alt_count,
            },
            'checks': variant_checks_list,
            'latest_check': latest_check,
            'latest_checks_agree': last_two_checks_agree,
            'comment_form': var_comment_form,
            'comments': variant_comments_list,
            'final_decision': sample_variant.variant_instance.get_final_decision_display(),
            'manual_upload': sample_variant.variant_instance.manual_upload,
        }

        # add to poly list if appears in the poly variant list, otherwise add to variant calls list
        if 'Poly' in previous_classifications:
            polys_list.append(variant_calls_dict)
        else:
            variant_calls.append(variant_calls_dict)


    variant_data = {
        'variant_calls': variant_calls, 
        'polys': polys_list,
        'check_options': VariantCheck.DECISION_CHOICES,
    }

    return variant_data



def get_fusion_info(sample_data,sample_obj):

    fusions = FusionPanelAnalysis.objects.filter(sample_analysis= sample_obj)

    fusion_calls = []
    for fusion_object in fusions:

        # TODO this is only needed for seeing variants in other runs - removed to speed up DB
        #this_run = FusionAnalysis.objects.filter(
        #    fusion_genes=fusion_object.fusion_instance.fusion_genes,
        #    sample__worksheet__run__run_id=sample_data.get('run_id')
        #)
        #this_run_count = this_run.count()

        #total_runs = FusionAnalysis.objects.filter(sample__worksheet__run__run_id=sample_data.get('run_id'))
        #total_runs_count = total_runs.count()

        # get checks for each variant
        fusion_checks = FusionCheck.objects.filter(fusion_analysis=fusion_object)
        fusion_checks_list = [ v.get_decision_display() for v in fusion_checks ]
        latest_check = fusion_checks.latest('pk')

        # do the last two checks agree?
        last_two_checks_agree = True
        if len(fusion_checks_list) > 1:
            last2 = fusion_checks_list[-2:]
            # skip check if not analysed
            if last2[1] != 'Not analysed':
                if last2[0] != last2[1]:
                    last_two_checks_agree = False

        fusion_comment_form = FusionCommentForm(
            pk=latest_check.pk, 
            hgvs= fusion_object.fusion_instance.hgvs, 
            comment=latest_check.comment
        )

        # get list of comments for variant
        fusion_comments_list = []
        for v in fusion_checks:
            if v.comment:
                fusion_comments_list.append(
                    { 'comment': v.comment, 'user': v.check_object.user, 'updated': v.comment_updated, }
                )

        # TODO this is only needed if they want to see the number of reference reads
        #if fusion_object.fusion_instance.fusion_caller == 'Splice':
        #    reference_reads = fusion_object.fusion_instance.ref_reads_1
        #elif fusion_object.fusion_instance.fusion_caller == 'Fusion':
        #    reference_reads = f'{fusion_object.fusion_instance.ref_reads_1} | {fusion_object.fusion_instance.ref_reads_2}'

        fusion_calls_dict = {
            'pk': fusion_object.pk,
            'fusion_instance_pk': fusion_object.fusion_instance.pk,
            'fusion_genes': fusion_object.fusion_instance.fusion_genes.fusion_genes,
            'fusion_hgvs': fusion_object.fusion_instance.hgvs,
            'fusion_supporting_reads': fusion_object.fusion_instance.fusion_supporting_reads,
            'left_breakpoint': fusion_object.fusion_instance.fusion_genes.left_breakpoint,
            'right_breakpoint': fusion_object.fusion_instance.fusion_genes.right_breakpoint,
            #'reference_reads': reference_reads,
            'this_run': {
                #'count': this_run_count, 
                #'total': total_runs_count,
                'ntc': fusion_object.fusion_instance.in_ntc,
            },   
            'checks': fusion_checks_list,
            'latest_check': latest_check,
            'latest_checks_agree': last_two_checks_agree,
            'comment_form': fusion_comment_form,
            'comments': fusion_comments_list,
            'final_decision': fusion_object.fusion_instance.get_final_decision_display()
                

        }

        fusion_calls.append(fusion_calls_dict)

    fusion_data = {'fusion_calls': fusion_calls, 'check_options': FusionCheck.DECISION_CHOICES, }

    return fusion_data



def get_coverage_data(sample_obj):
    #create a coverage dictionary
    coverage_data = {}
    gene_coverage_analysis_obj = GeneCoverageAnalysis.objects.filter(sample=sample_obj).order_by('gene')

    for gene_coverage_obj in gene_coverage_analysis_obj:

        regions = []
        coverage_regions_analysis_obj = RegionCoverageAnalysis.objects.filter(gene=gene_coverage_obj)
        for region in coverage_regions_analysis_obj:
            regions_dict = {
                'hgvs_c': region.hgvs_c,
                'average_coverage': region.average_coverage,
                'hotspot_or_genescreen': region.get_hotspot_display(),
                'percent_135x': region.percent_135x,
                'percent_270x': region.percent_270x,
                'ntc_coverage': region.ntc_coverage,
                'percent_ntc': region.percent_ntc,
            }
            regions.append(regions_dict)

        # Create a dictionary of gaps in the sample for the given gene
        gaps_270 = []
        gaps_135 = []
        gaps_analysis_obj=GapsAnalysis.objects.filter(gene=gene_coverage_obj)
        for gap in gaps_analysis_obj:
            if gap.coverage_cutoff == 270:
                gaps_dict = {
                    'genomic': gap.genomic(),
                    'hgvs_c': gap.hgvs_c,
                    'percent_cosmic': gap.percent_cosmic
                }
                gaps_270.append(gaps_dict)
            elif gap.coverage_cutoff == 135:
                gaps_dict = {
                    'genomic': gap.genomic(),
                    'hgvs_c': gap.hgvs_c,
                    'percent_cosmic': gap.percent_cosmic
                }
                gaps_135.append(gaps_dict)

        # combine gaps and regions dictionaries
        gene_dict = {
            'av_coverage': gene_coverage_obj.av_coverage,
            'percent_270x': gene_coverage_obj.percent_270x,
            'percent_135x': gene_coverage_obj.percent_135x,
            'av_ntc_coverage': gene_coverage_obj.av_ntc_coverage,
            'percent_ntc': gene_coverage_obj.percent_ntc,
            'regions': regions,
            'gaps_270': gaps_270,
            'gaps_135': gaps_135,
        }

        coverage_data[gene_coverage_obj.gene.gene] = gene_dict
        
    return coverage_data


def myeloid_add_to_dict(input_dict, anno):
    """
    Create a dictionary from the output in the create_myeloid_coverage_summary function in the 
    format:

        gene: {
            transcript: [regions]
        }...
    """

    # extract gene, exon and reference sequence from the input annotation
    gene_and_ref, exon = anno.split(':')
    exon = exon.replace('_', ' ')
    gene = gene_and_ref.split('(')[0]
    ref = gene_and_ref.split('(')[1]. split(')')[0]

    # if the gene is already in the dictionary
    if gene in input_dict.keys():

        # if the transcript is already in the dictionary, append to list
        if ref in input_dict[gene].keys():
            input_dict[gene][ref].append(exon)

        # otherwise make a new list for that transcript
        else:
            input_dict[gene][ref] = [exon]

    # if the gene isnt in the dict yet, add to dict
    else:
        input_dict[gene] = {ref: [exon]}

    return input_dict


def myeloid_format_output(input_dict):
    """
    Format the output of the dictionary created in the create_myeloid_coverage_summary function 
    into a sentence suitable for reporting

    """

    # a list of transcripts that aren't primary transcripts, these will be added after the gene in brackets
    # (primary transcripts aren't included)
    alt_transcripts = ['NM_153759.3', 'NM_001122607.1']

    # list to store output
    out_list = []

    # loop through each transcript within each gene
    for gene, values in sorted(input_dict.items()):
        for transcript, regions in values.items():

            # split the annotations into codons or exons and add exon/codon number to lists
            codons = []
            exons = []
            for r in regions:
                region = r.split(' ')[0]
                num = r.split(' ')[1]
                if region == 'exon':
                    exons.append(int(num))
                elif region == 'codon':
                    codons.append(num)

            # empty list to build output
            all_regions_list = []

            # add codons to list first, if there are any (these arent sorted if there are multiple)
            if codons:
                all_codons = f'codon {", ".join(codons)}'
                all_regions_list.append(all_codons)

            # add exons to list if there are any
            if exons:

                # handle pluralisation of word exon
                if len(exons) == 1:
                    all_exons = 'exon '
                else:
                    all_exons = 'exons '

                # sort and concatenate all exons
                exons_str = [str(exon) for exon in sorted(exons)]
                all_exons += ', '.join(exons_str)

                # add to list
                all_regions_list.append(all_exons)

            # combine codon and exon lists into one
            all_regions = ', '.join(all_regions_list)

            # add to the output list. if the transcript isnt a primary transcript, add the transcript ID in brackets after the gene name
            if transcript in alt_transcripts:
                out_list.append(f'{gene} ({transcript}) {all_regions}')
            else:
                out_list.append(f'{gene} {all_regions}')

    # format the output list as a sentence. If empty then return N/A
    if len(out_list) == 0:
        formatted_output = 'N/A'
    else:
        formatted_output = '; '.join(out_list) + '.'

    return formatted_output


def create_myeloid_coverage_summary(sample_obj):
    """
    Pull all regions (i.e. exons or hotspots) from all genes and format into a coverage summary sentence
    for copying into the report

    """

    # create empty dicts for storing output
    regions_with_zero = {}
    regions_with_less_270 = {}

    # get all gene coverage objects
    gene_coverage_analysis_obj = GeneCoverageAnalysis.objects.filter(sample=sample_obj)

    # loop through each region within each gene
    for gene_coverage_obj in gene_coverage_analysis_obj:
        coverage_regions_analysis_obj = RegionCoverageAnalysis.objects.filter(gene=gene_coverage_obj)
        for region_obj in coverage_regions_analysis_obj:

            # pull out the percent coverage at 270X and HGVS annotations
            cov = region_obj.percent_270x
            anno = region_obj.hgvs_c

            # only enter loop if coverage is less than 100% at 270X
            if cov < 100:

                # if no coverage at all at 270X
                if cov == 0:
                    myeloid_add_to_dict(regions_with_zero, anno)

                # if coverage is between 0-100% at 270X
                else:
                    myeloid_add_to_dict(regions_with_less_270, anno)

    # reformat as a sentence for output and add to output dictionary
    myeloid_coverage_summary = {
            'summary_0x': myeloid_format_output(regions_with_zero),
            'summary_270x': myeloid_format_output(regions_with_less_270),
        }

    return myeloid_coverage_summary
