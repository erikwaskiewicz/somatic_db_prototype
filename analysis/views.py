from django.shortcuts import render, redirect
from django.http import Http404

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .forms import SearchForm, NewVariantForm, SubmitForm, VariantCommentForm, UpdatePatientName, CoverageCheckForm, CheckPatientName
from .models import *
from .test_data import dummy_dicts
from .utils import signoff_check, make_next_check, get_variant_info, get_coverage_data, get_sample_info

import json
    

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
def analysis_sheet(request, sample_id):
    """
    Display coverage and variant metrics to allow checking of data 
    in IGV
    """
    # load in data that is common to both RNA and DNA workflows
    sample_obj = SampleAnalysis.objects.get(pk = sample_id)
    sample_data = get_sample_info(sample_obj)

    # assign to whoever clicked the sample and reload check objects
    current_step_obj = sample_data['checks']['current_check_object']
    if current_step_obj.user == None:
        current_step_obj.user = request.user
        current_step_obj.save()
        sample_data['checks'] = sample_obj.get_checks()
        
    # set up context dictionary
    context = {
        'success': [],
        'warning': [],
        'sample_data': sample_data,
        'new_variant_form': NewVariantForm(),
        'submit_form': SubmitForm(),
        'update_name_form': UpdatePatientName(),
        'check_name_form': CheckPatientName(),
        'coverage_check_form': CoverageCheckForm(comment=''),
    } #TODO pull comment through

    # DNA workflow
    if sample_data['dna_or_rna'] == 'DNA':
        context['variant_data'] = get_variant_info(sample_data, sample_obj)
        context['coverage_data'] = get_coverage_data(sample_obj)

    # RNA workflow
    elif sample_data['dna_or_rna'] == 'RNA':

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
                    'ntc': fusion_object.in_ntc,
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

        # patient name input form
        if 'name' in request.POST:
            update_name_form = UpdatePatientName(request.POST)

            if update_name_form.is_valid():
                new_name = update_name_form.cleaned_data['name']
                Sample.objects.filter(pk=sample_obj.sample.pk).update(sample_name=new_name)
                sample_obj = SampleAnalysis.objects.get(pk = sample_id)
                context['sample_data'] = get_sample_info(sample_obj)

        #check patient name update button
        if 'checker_comment' in request.POST:
            check_name_form = CheckPatientName(request.POST)

            if check_name_form.is_valid():
                checker_comment = check_name_form.cleaned_data['checker_comment']
                Sample.objects.filter(pk=sample_obj.sample.pk).update(sample_name_check=True)

        # comments submit button
        if 'variant_comment' in request.POST:
            new_comment = request.POST['variant_comment']
            pk = request.POST['pk']

            # update comment
            VariantCheck.objects.filter(pk=request.POST['pk']).update(
                comment=request.POST['variant_comment'],
                comment_updated=timezone.now(),
            )

            # reload variant data
            context['variant_data'] = get_variant_info(sample_data, sample_obj)


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
                if sample_data['sample_name'] == None:
                    context['warning'].append('Did not finialise check - input patient name before continuing')

                else:
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
                                    context['warning'].append('Did not finialise check - not all variant have been checked')
                                
                            # if 2nd IGV (or 3rd...) make interpretation
                            else:
                                if signoff_check(request.user, current_step_obj):
                                    make_next_check(sample_obj, 'VUS')
                                    return redirect('view_samples', sample_data['worksheet_id'])
                                else:
                                    context['warning'].append('Did not finialise check - not all variant have been checked')

                        # if interpretation, make complete
                        elif 'Interpretation' in current_step:
                            if signoff_check(request.user, current_step_obj):
                                return redirect('view_samples', sample_data['worksheet_id'])
                            else:
                                context['warning'].append('Did not finialise check - not all variant have been checked')


                    elif next_step == 'Request extra check':
                        if 'IGV' in current_step:
                            # make extra IGV check
                            if signoff_check(request.user, current_step_obj):
                                make_next_check(sample_obj, 'IGV')
                                return redirect('view_samples', sample_data['worksheet_id'])
                            else:
                                context['warning'].append('Did not finialise check - not all variant have been checked')

                        # throw error, cant do this yet
                        elif 'Interpretation' in current_step:
                            context['warning'].append("Only one interpretation check is carried out within this database, please only select eith 'Complete check' or 'Fail sample'")
                            # dont redirect - need to keep on current screen

                    elif next_step == 'Fail sample':
                        signoff_check(request.user, current_step_obj, 'F')
                        return redirect('view_samples', sample_data['worksheet_id'])


    # render the pages
    if sample_data['dna_or_rna'] == 'DNA':
        return render(request, 'analysis/analysis_sheet_dna.html', context)
    if sample_data['dna_or_rna'] == 'RNA':
        return render(request, 'analysis/analysis_sheet_rna.html', context)

    else:
        raise Http404(f'Sample must be either DNA or RNA, not {sample_data["dna_or_rna"]}')


def ajax(request):
    if request.is_ajax():

        sample_pk = request.POST.get('sample_pk')
        sample_obj = SampleAnalysis.objects.get(pk = sample_pk)
        dna_or_rna = sample_obj.sample.sample_type

        selections = json.loads(request.POST.get('selections'))

        for variant in selections:
            variant_obj = VariantPanelAnalysis.objects.get(pk=variant)
            current_check = variant_obj.get_current_check()
            igv_or_vus = current_check.check_object.stage

            if igv_or_vus == 'IGV':
                new_choice = selections[variant]['genuine_dropdown']
                current_check.decision = new_choice
                current_check.save()
            elif igv_or_vus == 'VUS':
                actionable_choice = selections[variant]['actionable_dropdown']
                vus_choice = selections[variant]['tier_dropdown']

        # dont think this redirect is doing anything but there needs to be a HTML response
        # actual reidrect is handled inside AJAX call in analysis-snvs.html
        return redirect('analysis_sheet', sample_pk)
