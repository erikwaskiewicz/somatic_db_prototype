from django.shortcuts import render, redirect
from django.http import Http404

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .forms import SearchForm, NewVariantForm, SubmitForm
from .models import *
from .test_data import dummy_dicts


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
    sample_obj = SampleAnalysis.objects.get(pk = sample_id)
    print(sample_obj)
    sample_data = {
        'sample_id': sample_obj.sample.sample_id,
        'worksheet_id': sample_obj.worksheet.ws_id,
        'panel': sample_obj.panel.panel_name,
        'run_id': sample_obj.worksheet.run.run_id,
        'checks': sample_obj.get_checks(),
    }

    # load in dummy data 
    # TODO - add, variant and coverage query, only patient info being queried at the mo
    #context = dummy_dicts.analysis_sheet_dict
    context={}
    context['sample_data'] = sample_data
    context['new_variant_form'] = NewVariantForm()
    context['submit_form'] = SubmitForm()

    if request.method == 'POST':

        # if add new variant form is clicked
        if 'hgvs_g' in request.POST:
            new_variant_form = NewVariantForm(request.POST)

            if new_variant_form.is_valid():
                # TODO need to program function & make more robust
                print(new_variant_form.cleaned_data)


        # if finalise check submit for is clicked
        if 'next_step' in request.POST:
            submit_form = SubmitForm(request.POST)

            if submit_form.is_valid():
                next_step = submit_form.cleaned_data['next_step']
                current_step = sample_data['checks']['current_status']
                current_step_obj = sample_data['checks']['current_check_object']

                if next_step == 'Complete check':
                    # TODO - signoff check
                    
                    if 'IGV' in current_step:
                        # TODO - if 1st IGV, make 2nd IGV
                        if current_step == 'IGV check 1':
                            print('TODO - if 1st IGV, make 2nd IGV')
                            print(current_step_obj)
                            
                        # TODO - if 2nd IGV (or 3rd...) make interpretation
                        else:
                            print('TODO - if 2nd IGV (or 3rd...) make interpretation')

                    # TODO - if interpretation, make complete
                    elif 'Interpretation' in current_step:
                        print('TODO - if interpretation, make complete')

                elif next_step == 'Request extra check':
                    # TODO - signoff check
                    
                    if 'IGV' in current_step:
                        # TODO - make extra IGV check
                        print('TODO - make extra IGV check')

                    # TODO - throw error, cant do this yet
                    elif 'Interpretation' in current_step:
                        print('TODO - throw error, cant do this yet')

                elif next_step == 'Fail sample':
                    print('3')

                return redirect('view_samples', sample_data['worksheet_id'])


    # DNA workflow
    if dna_or_rna == 'DNA':

        sample_variants=variant_analysis.objects.filter(sampleId= sample_data.get('sample_id'))

        variant_calls=[]

        for sample_variant in sample_variants.iterator():

            this_run=variant_analysis.objects.filter(variant= sample_variant.variant).filter(run=sample_data.get('run_id'))
            this_run_count=(this_run.count())

            previous_runs=variant_analysis.objects.filter(variant= sample_variant.variant).exclude(run=sample_data.get('run_id'))
            previous_runs_count=(previous_runs.count())

            total_runs=variant_analysis.objects.filter(variant= sample_variant.variant)
            total_runs_count=(total_runs.count())


            variant_calls_dict={
            'genomic': sample_variant.variant.genomic ,
            'gene': sample_variant.variant.gene ,
            'exon': sample_variant.variant.exon ,
            'transcript': sample_variant.variant.transcript,
            'hgvs_c': sample_variant.variant.hgvs_c ,
            'hgvs_p': sample_variant.variant.hgvs_p,
            'this_run': {
                        'count': this_run_count, 
                        'total': total_runs_count,
                    },   
            'previous_runs': {
                        'count': previous_runs_count,
            },

            }


            variant_calls.append(variant_calls_dict)

        polys_list=[]

        for sample_variant in sample_variants.iterator():

            known_polys=polys.objects.filter(genomic= sample_variant.variant.genomic)

            for known_poly in known_polys:
                polys_dict={
                    'genomic': known_poly.genomic,
                    'gene': known_poly.gene ,
                    'exon': known_poly.exon,
                    'transcript': known_poly.transcript ,
                    'hgvs_c': known_poly.hgvs_c,
                    'hgvs_p': known_poly.hgvs_p,

    
            }

                polys_list.append(polys_dict)



        coverage_data={}
        gene_coverage_analysis_obj=gene_coverage_analysis.objects.filter(sample= sample_data.get('sample_id'))
        for gene_coverage_obj in gene_coverage_analysis_obj.iterator():
            regions=[]
            coverage_regions_analysis_obj=coverage_regions_analysis.objects.filter(sample= sample_data.get('sample_id')).filter(gene=gene_coverage_obj.gene)
            for region in coverage_regions_analysis_obj.iterator():
                regions_dict={
                'genomic':region.genomic.genomic,

                }

                regions.append(regions_dict)




            gene_dict ={
                'av_coverage': 300,
                'percent_270x': gene_coverage_obj.percent_270x,
                'percent_135x': gene_coverage_obj.percent_135x,
                'regions':regions

            }

            coverage_data[gene_coverage_obj.gene.gene]=gene_dict




        variant_data={'variant_calls':variant_calls, 'polys': polys_list }
        context['variant_data']=variant_data
        context['coverage_data']=coverage_data
        print(context)
        return render(request, 'analysis/analysis_sheet_dna.html', context)

    # RNA workflow
    elif dna_or_rna == 'RNA':
        return render(request, 'analysis/analysis_sheet_rna.html', context)

    # return error if sample type is neither RNA or DNA
    else:
        raise Http404(f'Sample must be either DNA or RNA, not {dna_or_rna}')
