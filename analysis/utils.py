from .models import *
from .forms import SearchForm, NewVariantForm, SubmitForm, VariantCommentForm

from django.utils import timezone

# TODO make sure that nothing gets saved to db if there's an error -- ? transaction.atomic
def signoff_check(user, current_step_obj, status='C'):
    """

    """
    # make sure each variant has a class
    variant_checks = VariantCheck.objects.filter(check_object=current_step_obj)
    for v in variant_checks:
        if v.decision == '-':
            # this trigers view to render the error on the page
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

    # make check objects for all variants
    variant_objects = VariantAnalysis.objects.filter(sample=sample_obj)
    for v in variant_objects:
        new_variant_check = VariantCheck(
            variant_analysis = v,
            check_object = new_check_obj,
        )
        new_variant_check.save()

    return True


def get_variant_info(sample_data, sample_obj):

    sample_variants = VariantAnalysis.objects.filter(sample=sample_obj)

    variant_calls=[]
    polys_list=[]

    for sample_variant in sample_variants:

        #count how many times variant is present in other samples on the run
        this_run = VariantAnalysis.objects.filter(
            variant= sample_variant.variant,
            sample__worksheet__run__run_id=sample_data.get('run_id'),
        )
        this_run_count = this_run.count()

        # TODO - we're going to add this last
        #count how many times the variant is present in previous runs
        #previous_runs = VariantAnalysis.objects.filter(variant= sample_variant.variant).exclude(run=sample_data.get('run_id'))
        #previous_runs_count = previous_runs.count()

        #get the total number of samples on the run TODO - look into this, doesnt look like its working as expected
        total_runs = VariantAnalysis.objects.filter(sample__worksheet__run__run_id=sample_data.get('run_id'))
        total_runs_count = total_runs.count()

        # get whether the variant falls within a poly/ known list
        # TODO - will have to handle multiple poly/ known lists in future
        variant_obj = Variant.objects.get(genomic_37=sample_variant.variant.genomic_37)
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
        var_comment_form = VariantCommentForm(pk=latest_check.pk, comment=latest_check.comment)

        variant_comments_list = []
        for v in variant_checks:
            if v.comment:
                variant_comments_list.append(
                    { 'comment': v.comment, 'user': v.check_object.user, 'updated': v.comment_updated, }
                )

        #Create a variant calls dictionary to pass to analysis-snvs.html
        variant_calls_dict = {
            'pk': sample_variant.pk,
            'genomic': sample_variant.variant.genomic_37,
            'gene': sample_variant.variant.gene,
            'exon': sample_variant.variant.exon,
            'transcript': sample_variant.variant.transcript,
            'hgvs_c': sample_variant.variant.hgvs_c,
            'hgvs_p': sample_variant.variant.hgvs_p,
            'this_run': {
                'count': this_run_count, 
                'total': total_runs_count,
                'ntc': True,
            },   
            'previous_runs': {
                'known': ' | '.join(previous_classifications),
                'count': '1', #previous_runs_count,
            },
            'vaf': {
                'vaf': sample_variant.vaf,
                'total_count': sample_variant.total_count,
                'alt_count': sample_variant.alt_count,
            },
            'checks': variant_checks_list,
            'latest_check': latest_check,
            'comment_form': var_comment_form,
            'comments': variant_comments_list,
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
        #print(regions)

        # Create a dictionary of gaps in the sample for the given gene
        gaps_270 = []
        gaps_135 = []
        gaps_analysis_obj=GapsAnalysis.objects.filter(gene=gene_coverage_obj)
        for gap in gaps_analysis_obj:
            if gap.coverage_cutoff == 270:
                gaps_dict = {
                    'genomic': gap.genomic,
                    'hgvs_c': gap.hgvs_c,
                    'percent_cosmic': gap.percent_cosmic
                }
                gaps_270.append(gaps_dict)
            elif gap.coverage_cutoff == 135:
                gaps_dict = {
                    'genomic': gap.genomic,
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
