from django.shortcuts import render, redirect
from django.http import Http404

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .forms import SearchForm, NewVariantForm, SubmitForm
from .models import *
from .test_data import dummy_dicts
from .utils import signoff_check, make_next_check


def signup(request):
    """
    Allow users to sign up
    User accounts are inactive by default - an admin must activate it using the admin page.
    """

    form = UserCreationForm()
    warnings = []

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():

            form.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            #user.is_active = False TODO - uncomment this when we go live
            user.save()

            return redirect('home')
            #TODO - add some kind of confirmation

        else:
            warnings.append('Could not create an account, check that your password meets the requirements below')

    return render(request, 'analysis/sign-up.html', {'form': form, 'warning': warnings})


@login_required
def home(request):
    """
    TODO - no home page yet, just redirect to list of worksheets
    """
    return redirect('view_worksheets')


@login_required
def view_worksheets(request):
    """
    Displays all worksheets and links to the page to show all samples 
    within the worksheet
    """
    worksheets = Worksheet.objects.all()
    ws_list = []
    for w in worksheets:
        ws_list.append({
            'worksheet_id': w.ws_id,
            'run_id': w.run.run_id,
            'assay': w.assay,
            'status': w.get_status(),
        })

    context = {
        'worksheets': ws_list,
        'search_form': SearchForm(),
    }

    return render(request, 'analysis/view_worksheets.html', context)


@login_required
def view_samples(request, worksheet_id):
    """
    Displays all samples with a worksheet and links to the analysis 
    for the sample
    """
    samples = SampleAnalysis.objects.filter(worksheet = worksheet_id)
    sample_dict = {}
    for s in samples:
        sample_id = s.sample.sample_id
        if sample_id not in sample_dict.keys():
            sample_dict[sample_id] = {
                'sample_id': sample_id,
                'dna_rna': s.sample.sample_type,
                'panels': [
                    {
                        'analysis_id': s.pk,
                        'panel': s.panel.panel_name,
                        'checks': s.get_checks(),
                    }
                ]
            }
        else:
            sample_dict[sample_id]['panels'].append(
                {
                    'analysis_id': s.pk,
                    'panel': s.panel.panel_name,
                    'checks': s.get_checks(),
                }
            )

    context = {
        'worksheet': worksheet_id,
        'samples': sample_dict,
        'search_form': SearchForm(),
    }

    return render(request, 'analysis/view_samples.html', context)


@login_required
def analysis_sheet(request, dna_or_rna, sample_id):
    """
    Display coverage and variant metrics to allow checking of data 
    in IGV
    """
    # load in data that is common to both RNA and DNA workflows
    sample_obj = SampleAnalysis.objects.get(pk = sample_id)

    sample_data = {
        'sample_id': sample_obj.sample.sample_id,
        'worksheet_id': sample_obj.worksheet.ws_id,
        'panel': sample_obj.panel.panel_name,
        'run_id': sample_obj.worksheet.run.run_id,
        'checks': sample_obj.get_checks(),
    }

    # assign to whoever clicked the sample and reload check objects
    current_step_obj = sample_data['checks']['current_check_object']
    if current_step_obj.user == None:
        current_step_obj.user = request.user
        current_step_obj.save()
        sample_data['checks'] = sample_obj.get_checks()
        

    context = {
        'success': [],
        'warning': [],
        'sample_data': sample_data,
        'new_variant_form': NewVariantForm(),
        'submit_form': SubmitForm(),
    }


    # DNA workflow
    if dna_or_rna == 'DNA':

        sample_variants = VariantAnalysis.objects.filter(
            sample=sample_obj,
        )

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

            #get the total number of samples on the run
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
            print(variant_checks)
            variant_comments_list = []
            for v in variant_checks:
                if v.comment:
                    variant_comments_list.append(
                        {'comment': v.comment, 'user': v.check_object.user}
                    )

            #Create a variant calls dictionary to pass to analysis-snvs.html
            variant_calls_dict = {
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
                'comments': variant_comments_list,
            }

            # add to poly list if appears in the poly variant list, otherwise add to variant calls list
            if 'Poly' in previous_classifications:
                polys_list.append(variant_calls_dict)
            else:
                variant_calls.append(variant_calls_dict)


        #create a coverage dictionary
        coverage_data = {}
        gene_coverage_analysis_obj = GeneCoverageAnalysis.objects.filter(sample=sample_obj)

        for gene_coverage_obj in gene_coverage_analysis_obj:

            regions = []
            coverage_regions_analysis_obj = CoverageRegionsAnalysis.objects.filter(sample=sample_obj)
            for region in coverage_regions_analysis_obj:
                regions_dict = {
                    'genomic': region.genomic.genomic,
                    'average_coverage': region.average_coverage,
                    'percent_135x': region.percent_135x,
                    'percent_270x': region.percent_270x,
                    'ntc_coverage': region.ntc_coverage,
                    'percent_ntc': region.percent_ntc,
                }
                regions.append(regions_dict)

            # Create a dictionary of gaps in the sample for the given gene
            gaps = []
            gaps_analysis_obj=GapsAnalysis.objects.filter(sample=sample_obj)
            for gap in gaps_analysis_obj:
                gaps_dict = {
                    'genomic': gap.genomic.genomic,
                    'average_coverage': gap.percent_135x,
                    'percent_135x': gap.percent_135x,
                    'percent_270x': gap.percent_270x,
                    'average_coverage': gap.average_coverage,
                    'percent_cosmic': gap.percent_cosmic
                }
                gaps.append(gaps_dict)

            # combine gaps and regions dictionaries
            gene_dict = {
                'av_coverage': '300',
                'percent_270x': gene_coverage_obj.percent_270x,
                'percent_135x': gene_coverage_obj.percent_135x,
                'av_ntc_coverage': gene_coverage_obj.av_ntc_coverage,
                'percent_ntc': gene_coverage_obj.percent_ntc,
                'regions': regions,
                'gaps': gaps,
            }

            coverage_data[gene_coverage_obj.gene.gene] = gene_dict

        # add variant and coverage data to context dict
        context['variant_data'] = {
            'variant_calls': variant_calls, 
            'polys': polys_list,
        }
        context['coverage_data'] = coverage_data


    # RNA workflow
    elif dna_or_rna == 'RNA':

        fusions = FusionAnalysis.objects.filter(sample = sample_obj)

        fusion_calls=[]
        for fusion_object in fusions:

            this_run = FusionAnalysis.objects.filter(
                fusion_genes=fusion_object.fusion_genes,
                sample__worksheet__run__run_id=sample_data.get('run_id')
            )
            this_run_count = this_run.count()

            total_runs = FusionAnalysis.objects.filter(sample__worksheet__run__run_id=sample_data.get('run_id'))
            total_runs_count = total_runs.count()

            # TODO were leaving this til last
            #previous_runs = FusionAnalysis.objects.filter(fusion_genes=fusion_object.fusion_genes).exclude(sample__worksheet__run__run_id=sample_data.get('run_id'))
            #previous_runs_count = previous_runs.count()

            fusion_calls_dict = {
                'fusion_genes': fusion_object.fusion_genes.fusion_genes,
                'split_reads': fusion_object.split_reads,
                'spanning_reads': fusion_object.spanning_reads,
                'left_breakpoint': fusion_object.fusion_genes.left_breakpoint,
                'right_breakpoint': fusion_object.fusion_genes.right_breakpoint,
                'this_run': {
                    'count': this_run_count, 
                    'total': total_runs_count,
                    'ntc': True,
                },   
                'previous_runs': {
                    'count': '1',
                },
            }

            fusion_calls.append(fusion_calls_dict)

        context['fusion_data'] = {'fusion_calls': fusion_calls}


    ###  If any buttons are pressed
    ####################################
    if request.method == 'POST':

        # if add new variant form is clicked
        if 'hgvs_g' in request.POST:
            new_variant_form = NewVariantForm(request.POST)

            if new_variant_form.is_valid():
                # TODO need to program function & make more robust
                print(new_variant_form.cleaned_data)


        # if finalise check submit form is clicked
        if 'next_step' in request.POST:
            submit_form = SubmitForm(request.POST)

            if submit_form.is_valid():
                next_step = submit_form.cleaned_data['next_step']
                current_step = sample_data['checks']['current_status']

                if next_step == 'Complete check':
                    if 'IGV' in current_step:
                        # if 1st IGV, make 2nd IGV
                        if current_step == 'IGV check 1':
                            if signoff_check(request.user, current_step_obj):
                                make_next_check(sample_obj, 'IGV')
                                return redirect('view_samples', sample_data['worksheet_id'])
                            else:
                                context['warning'].append('Not all variant have been checked')
                            
                        # if 2nd IGV (or 3rd...) make interpretation
                        else:
                            if signoff_check(request.user, current_step_obj):
                                make_next_check(sample_obj, 'VUS')
                                return redirect('view_samples', sample_data['worksheet_id'])
                            else:
                                context['warning'].append('Not all variant have been checked')

                    # if interpretation, make complete
                    elif 'Interpretation' in current_step:
                        if signoff_check(request.user, current_step_obj):
                            return redirect('view_samples', sample_data['worksheet_id'])
                        else:
                            context['warning'].append('Not all variant have been checked')


                elif next_step == 'Request extra check':
                    if 'IGV' in current_step:
                        # make extra IGV check
                        if signoff_check(request.user, current_step_obj):
                            make_next_check(sample_obj, 'IGV')
                            return redirect('view_samples', sample_data['worksheet_id'])
                        else:
                            context['warning'].append('Not all variant have been checked')

                    # throw error, cant do this yet
                    elif 'Interpretation' in current_step:
                        context['warning'].append("Only one interpretation check is carried out within this database, please only select eith 'Complete check' or 'Fail sample'")
                        # dont redirect - need to keep on current screen

                elif next_step == 'Fail sample':
                    signoff_check(request.user, current_step_obj, 'F')
                    return redirect('view_samples', sample_data['worksheet_id'])


    # render the pages
    if dna_or_rna == 'DNA':
        return render(request, 'analysis/analysis_sheet_dna.html', context)
    if dna_or_rna == 'RNA':
        return render(request, 'analysis/analysis_sheet_rna.html', context)
    else:
        raise Http404(f'Sample must be either DNA or RNA, not {dna_or_rna}')
