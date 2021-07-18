from .models import *
from .forms import SearchForm, NewVariantForm, SubmitForm, VariantCommentForm, FusionCommentForm

from django.utils import timezone

# TODO make sure that nothing gets saved to db if there's an error -- ? transaction.atomic
def signoff_check(user, current_step_obj, sample_obj, status='C'):
    """

    """
    # make sure each variant has a class
    if sample_obj.sample.sample_type == 'DNA':
        variant_checks = VariantCheck.objects.filter(check_object=current_step_obj)
    elif sample_obj.sample.sample_type == 'RNA':
        variant_checks = FusionCheck.objects.filter(check_object=current_step_obj)

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
        'run_id': sample_obj.worksheet.run.run_id,
        'total_reads': sample_obj.sample.total_reads,
        'total_reads_ntc': sample_obj.sample.total_reads_ntc,
        'percent_reads_ntc': sample_obj.sample.percent_reads_ntc,
        'checks': sample_obj.get_checks(),
    }
    return sample_data


def get_variant_info(sample_data, sample_obj):

    sample_variants = VariantPanelAnalysis.objects.filter(sample_analysis=sample_obj)

    variant_calls = []
    polys_list = []

    # get list of other samples on the run
    current_run_obj = sample_obj.worksheet.run
    current_run_samples = SampleAnalysis.objects.filter(worksheet__run = current_run_obj)
    # remove dups
    sample_objects = set([ s.sample for s in current_run_samples ])

    for sample_variant in sample_variants:

        variant_obj = sample_variant.variant_instance.variant

        # count how many times variant is present in other samples on the run
        this_run_count = 0
        for s in sample_objects:
            qs = VariantInstance.objects.filter(
                sample = s,
                variant = variant_obj,
            )
            if qs:
                this_run_count += 1

        # TODO - we're going to add this last, need to exclude current run??
        '''#count how many times the variant is present in previous runs
        previous_runs = VariantInstance.objects.filter(
            variant = variant_obj
        ).count()
        print(previous_runs)'''

        # get whether the variant falls within a poly/ known list
        # TODO - will have to handle multiple poly/ known lists in future
        previous_classifications = []
        for l in VariantToVariantList.objects.filter(variant=variant_obj):
            if l.variant_list.name == 'TSO500_known':
                previous_classifications.append(l.classification)
            elif l.variant_list.name == 'TSO500_polys':
                previous_classifications.append('Poly')

        # get checks for each variant
        variant_checks = VariantCheck.objects.filter(variant_analysis=sample_variant)
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
            'genomic': variant_obj.genomic_37,
            'igv_coords': variant_obj.genomic_37.strip('ACGT>'),
            'gene': variant_obj.gene,
            'exon': variant_obj.exon,
            'transcript': variant_obj.transcript,
            'hgvs_c': variant_obj.hgvs_c,
            'hgvs_p': variant_obj.hgvs_p,
            'this_run': {
                'count': this_run_count, 
                'total': len(sample_objects),
                'ntc': sample_variant.variant_instance.in_ntc,
            },   
            'previous_runs': {
                'known': ' | '.join(previous_classifications),
                'count': '1', #previous_runs,
            },
            'vaf': {
                'vaf': sample_variant.variant_instance.vaf,
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

    fusion_calls=[]
    for fusion_object in fusions:

        this_run = FusionAnalysis.objects.filter(
            fusion_genes=fusion_object.fusion_instance.fusion_genes,
            sample__worksheet__run__run_id=sample_data.get('run_id')
        )
        this_run_count = this_run.count()

        total_runs = FusionAnalysis.objects.filter(sample__worksheet__run__run_id=sample_data.get('run_id'))
        total_runs_count = total_runs.count()


        # TODO were leaving this til last
        #previous_runs = FusionAnalysis.objects.filter(fusion_genes=fusion_object.fusion_genes).exclude(sample__worksheet__run__run_id=sample_data.get('run_id'))
        #previous_runs_count = previous_runs.count()

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
            comment=latest_check.comment)

        # get list of comments for variant
        fusion_comments_list = []
        for v in fusion_checks:
            if v.comment:
                fusion_comments_list.append(
                    { 'comment': v.comment, 'user': v.check_object.user, 'updated': v.comment_updated, }
                )

        fusion_calls_dict = {
            'pk': fusion_object.pk,
            'fusion_genes': fusion_object.fusion_instance.fusion_genes.fusion_genes,
            'fusion_hgvs': fusion_object.fusion_instance.hgvs,
            'fusion_supporting_reads': fusion_object.fusion_instance.fusion_supporting_reads,
            'left_breakpoint': fusion_object.fusion_instance.fusion_genes.left_breakpoint,
            'right_breakpoint': fusion_object.fusion_instance.fusion_genes.right_breakpoint,
            'this_run': {
                'count': this_run_count, 
                'total': total_runs_count,
                'ntc': fusion_object.fusion_instance.in_ntc,
            },   
            'previous_runs': {
            #TODO- this shouldn't be hardcoded
                'count': '1',
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
    gene_coverage_analysis_obj = GeneCoverageAnalysis.objects.filter(sample=sample_obj)

    for gene_coverage_obj in gene_coverage_analysis_obj:

        regions = []
        coverage_regions_analysis_obj = RegionCoverageAnalysis.objects.filter(gene=gene_coverage_obj)
        for region in coverage_regions_analysis_obj:
            regions_dict = {
                'hgvs_c': region.hgvs_c,
                'average_coverage': region.average_coverage,
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
