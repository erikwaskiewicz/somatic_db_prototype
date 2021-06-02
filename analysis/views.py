from django.shortcuts import render, redirect
from django.http import Http404

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .forms import SearchForm, NewVariantForm
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
    sample_data = {
        'sample_id': sample_obj.sample.sample_id,
        'worksheet_id': sample_obj.worksheet.ws_id,
        'panel': sample_obj.panel.panel_name,
        'run_id': sample_obj.worksheet.run.run_id,
        'checks': sample_obj.get_checks(),
    }

    # load in dummy data 
    # TODO - add, variant and coverage query, only patient info being queried at the mo
    context = dummy_dicts.analysis_sheet_dict
    context['sample_data'] = sample_data
    context['new_variant_form'] = NewVariantForm()

    if request.method == 'POST':

        if 'hgvs_g' in request.POST:
            new_variant_form = NewVariantForm(request.POST)

            if new_variant_form.is_valid():
                # TODO need to program function & make more robust
                print(new_variant_form.cleaned_data)


    # DNA workflow
    if dna_or_rna == 'DNA':
        return render(request, 'analysis/analysis_sheet_dna.html', context)

    # RNA workflow
    elif dna_or_rna == 'RNA':
        return render(request, 'analysis/analysis_sheet_rna.html', context)

    # return error if sample type is neither RNA or DNA
    else:
        raise Http404(f'Sample must be either DNA or RNA, not {dna_or_rna}')
