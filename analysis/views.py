from django.shortcuts import render, redirect
from django.http import Http404

from .forms import SearchForm, NewVariantForm
from .test_data import dummy_dicts


def home(request):
    """
    TODO - no home page yet, just redirect to list of worksheets
    """
    return redirect('view_worksheets')


def view_worksheets(request):
    """
    Displays all worksheets and links to the page to show all samples 
    within the worksheet
    """
    context = dummy_dicts.view_worksheets_dict
    context['search_form'] = SearchForm()

    return render(request, 'analysis/view_worksheets.html', context)


def view_samples(request, worksheet_id):
    """
    Displays all samples with a worksheet and links to the analysis 
    for the sample
    """
    context = dummy_dicts.view_samples_dict
    context['search_form'] = SearchForm()
    return render(request, 'analysis/view_samples.html', context)


def analysis_sheet(request, dna_or_rna, sample_id):
    """
    Display coverage and variant metrics to allow checking of data 
    in IGV
    """
    # load in dummy data
    context = dummy_dicts.analysis_sheet_dict
    context['new_variant_form'] = NewVariantForm()

    # DNA workflow
    if dna_or_rna == 'DNA':
        return render(request, 'analysis/analysis_sheet_dna.html', context)

    # RNA workflow
    elif dna_or_rna == 'RNA':
        return render(request, 'analysis/analysis_sheet_rna.html', context)

    # return error if sample type is neither RNA or DNA
    else:
        raise Http404(f'Sample must be either DNA or RNA, not {dna_or_rna}')
