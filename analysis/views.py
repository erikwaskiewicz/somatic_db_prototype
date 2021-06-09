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

    context = {
        'sample_data': sample_data,
        'new_variant_form': NewVariantForm(),
        'submit_form': SubmitForm(),
    }


    # DNA workflow
    if dna_or_rna == 'DNA':

        sample_variants=variant_analysis.objects.filter(sampleId= sample_data.get('sample_id')).filter(run=sample_data.get('run_id')).filter(panel=sample_data.get('panel'))

        variant_calls=[]

        for sample_variant in sample_variants.iterator():

            #count how many times variant is present in other samples on the run
            this_run=variant_analysis.objects.filter(variant= sample_variant.variant).filter(run=sample_data.get('run_id'))
            this_run_count=(this_run.count())

            #count how many times the variant is present in previous runs
            previous_runs=variant_analysis.objects.filter(variant= sample_variant.variant).exclude(run=sample_data.get('run_id'))
            previous_runs_count=(previous_runs.count())

            #get the total number of samples on the run
            total_runs=variant_analysis.objects.filter(run=sample_data.get('run_id'))
            total_runs_count=(total_runs.count())


            #Create a variant calls dictionary to pass to analysis-snvs.html
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
            'vaf': {
                        'vaf': sample_variant.vaf,
                        'total_count': sample_variant.total_count,
                        'alt_count': sample_variant.alt_count
                }
            }
            variant_calls.append(variant_calls_dict)


        #Create a polys dictionary
        polys_list=[]

        #loop through the sample variants and get all the polys from the database that have genomic coordinates matching the sample variant coordinates
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
                    'vaf': {
                        'vaf': sample_variant.vaf,
                        'total_count': sample_variant.total_count,
                        'alt_count': sample_variant.alt_count
                }
            }

                polys_list.append(polys_dict)


        #create a coverage dictionary
        coverage_data={}
        gene_coverage_analysis_obj=gene_coverage_analysis.objects.filter(sample= sample_data.get('sample_id')).filter(panel= sample_data.get('panel'))
        for gene_coverage_obj in gene_coverage_analysis_obj.iterator():
            regions=[]
            coverage_regions_analysis_obj=coverage_regions_analysis.objects.filter(sample= sample_data.get('sample_id')).filter(gene=gene_coverage_obj.gene).filter(panel= sample_data.get('panel'))
            for region in coverage_regions_analysis_obj.iterator():
                regions_dict={
                'genomic':region.genomic.genomic,
                'average_coverage': region.average_coverage,
                'percent_135x': region.percent_135x,
                'percent_270x': region.percent_270x,
                'ntc_coverage':region.ntc_coverage,
                'percent_ntc':region.percent_ntc,
                }

                regions.append(regions_dict)


            #Create a dictionary of gaps in the sample for the given gene
            gaps=[]
            gaps_analysis_obj=gaps_analysis.objects.filter(sample= sample_data.get('sample_id')).filter(gene=gene_coverage_obj.gene)
            for gap in gaps_analysis_obj.iterator():
                gaps_dict={
                'genomic':gap.genomic.genomic,
                'average_coverage': gap.percent_135x,
                'percent_135x': gap.percent_135x,
                'percent_270x': gap.percent_270x,
                'average_coverage':gap.average_coverage,
                'percent_cosmic':gap.percent_cosmic

                }

                gaps.append(gaps_dict)


            #combine gaps and regions dictionaries
            gene_dict ={
                'av_coverage': '300',
                'percent_270x': gene_coverage_obj.percent_270x,
                'percent_135x': gene_coverage_obj.percent_135x,
                'av_ntc_coverage': gene_coverage_obj.av_ntc_coverage,
                'percent_ntc': gene_coverage_obj.percent_ntc,
                'regions':regions,
                'gaps':gaps,
            }

            coverage_data[gene_coverage_obj.gene.gene]=gene_dict


        variant_data={'variant_calls':variant_calls, 'polys': polys_list }
        context['variant_data']=variant_data
        context['coverage_data']=coverage_data
        print(context)


    # RNA workflow
    elif dna_or_rna == 'RNA':

        fusions=fusion_analysis.objects.filter(sampleId= sample_data.get('sample_id')).filter(run=sample_data.get('run_id')).filter(panel=sample_data.get('panel'))

        fusion_calls=[]

        for fusion_object in fusions.iterator():

            this_run=fusion_analysis.objects.filter(fusion_genes= fusion_object.fusion_genes).filter(run=sample_data.get('run_id'))
            this_run_count=(this_run.count())

            previous_runs=fusion_analysis.objects.filter(fusion_genes= fusion_object.fusion_genes).exclude(run=sample_data.get('run_id'))
            previous_runs_count=(previous_runs.count())

            total_runs=fusion_analysis.objects.filter(run=sample_data.get('run_id'))
            total_runs_count=(total_runs.count())


            fusion_calls_dict={
            'fusion_genes': fusion_object.fusion_genes.fusion_genes,
            'split_reads': fusion_object.split_reads,
            'spanning_reads': fusion_object.spanning_reads,
            'left_breakpoint': fusion_object.fusion_genes.left_breakpoint ,
            'right_breakpoint': fusion_object.fusion_genes.right_breakpoint ,
            'this_run': {
                        'count': this_run_count, 
                        'total': total_runs_count,
                    },   
            'previous_runs': {
                        'count': previous_runs_count,
            },

            }

            fusion_calls.append(fusion_calls_dict)


            print(fusion_calls_dict)

        fusion_data={'fusion_calls':fusion_calls }
        context['fusion_data']=fusion_data


    ###  If any buttons are pressed
    ####################################
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
                    if 'IGV' in current_step:
                        # if 1st IGV, make 2nd IGV
                        if current_step == 'IGV check 1':
                            signoff_check(request.user, current_step_obj)
                            make_next_check(sample_obj, 'IGV')
                            
                        # if 2nd IGV (or 3rd...) make interpretation
                        else:
                            signoff_check(request.user, current_step_obj)
                            make_next_check(sample_obj, 'VUS')

                    # if interpretation, make complete
                    elif 'Interpretation' in current_step:
                        signoff_check(request.user, current_step_obj)

                    return redirect('view_samples', sample_data['worksheet_id'])


                elif next_step == 'Request extra check':
                    if 'IGV' in current_step:
                        # make extra IGV check
                        signoff_check(request.user, current_step_obj)
                        make_next_check(sample_obj, 'IGV')
                        return redirect('view_samples', sample_data['worksheet_id'])

                    # throw error, cant do this yet
                    elif 'Interpretation' in current_step:
                        context['warning'] = ["Only one interpretation check is carried out within this database, please only select eith 'Complete check' or 'Fail sample'"]
                        # dont redirect - need to keep on current screen

                elif next_step == 'Fail sample':
                    signoff_check(request.user, current_step_obj, 'F')
                    return redirect('view_samples', sample_data['worksheet_id'])


    if dna_or_rna == 'DNA':
        return render(request, 'analysis/analysis_sheet_dna.html', context)
    if dna_or_rna == 'RNA':
        return render(request, 'analysis/analysis_sheet_rna.html', context)
    else:
        raise Http404(f'Sample must be either DNA or RNA, not {dna_or_rna}')
