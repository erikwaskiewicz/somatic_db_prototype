from django.shortcuts import render, redirect
from django.http import Http404

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from .forms import SearchForm, NewVariantForm, SubmitForm, VariantCommentForm, UpdatePatientName, CoverageCheckForm, CheckPatientName, FusionCommentForm
from .models import *
from .test_data import dummy_dicts
from .utils import signoff_check, make_next_check, get_variant_info, get_coverage_data, get_sample_info, get_fusion_info
from django.template.loader import get_template
from xhtml2pdf import pisa 
from django.template import Context


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

    current_step_obj = sample_data['checks']['current_check_object']

    # assign to whoever clicked the sample and reload check objects
    if sample_data['checks']['current_status'] not in ['Complete', 'Fail']:
        if current_step_obj.user == None:
            current_step_obj.user = request.user
            current_step_obj.save()
            sample_data['checks'] = sample_obj.get_checks()

        if current_step_obj.user != request.user:
            raise PermissionDenied()
        
    # set up context dictionary
    context = {
        'success': [],
        'warning': [],
        'sample_data': sample_data,
        'new_variant_form': NewVariantForm(),
        'submit_form': SubmitForm(),
        'update_name_form': UpdatePatientName(),
        'check_name_form': CheckPatientName(),
        'coverage_check_form': CoverageCheckForm(
            pk=current_step_obj.pk, 
            comment=current_step_obj.coverage_comment,
            ntc_check=current_step_obj.coverage_ntc_check,
        ),

    } #TODO pull coverage comment through and display comments from all checkers

    # DNA workflow
    if sample_data['dna_or_rna'] == 'DNA':
        context['variant_data'] = get_variant_info(sample_data, sample_obj)
        context['coverage_data'] = get_coverage_data(sample_obj)



    # RNA workflow
    elif sample_data['dna_or_rna'] == 'RNA':
        context['fusion_data'] = get_fusion_info(sample_data, sample_obj)

        


    if request.method == 'GET':

        if 'download' in request.GET:

            template = get_template('analysis/analysis-report-dna.html')
            html  = template.render(context)



            file = open('test.pdf', "w+b")
            pisaStatus = pisa.CreatePDF(html, dest=file, encoding='utf-8')

            file.seek(0)
            pdf = file.read()
            file.close() 




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
                comment=new_comment,
                comment_updated=timezone.now(),
            )

            # reload variant data
            context['variant_data'] = get_variant_info(sample_data, sample_obj)

        # coverage comments button
        if 'coverage_comment' in request.POST:
            new_comment = request.POST['coverage_comment']
            try:
                if request.POST['ntc_checked'] == 'on':
                    ntc_checked = True
            except:
                ntc_checked = False
            pk = request.POST['pk']

            # update comment
            Check.objects.filter(pk=request.POST['pk']).update(
                coverage_comment=new_comment,
                coverage_comment_updated=timezone.now(),
                coverage_ntc_check=ntc_checked,
            )

            # reload sample data
            context['sample_data'] = get_sample_info(sample_obj)
            current_step_obj = context['sample_data']['checks']['current_check_object']
            context['coverage_check_form'] = CoverageCheckForm(
                pk=current_step_obj.pk, 
                comment=current_step_obj.coverage_comment,
                ntc_check=current_step_obj.coverage_ntc_check,
            )

        # fusion comments submit button
        if 'fusion_comment' in request.POST:
            new_comment = request.POST['fusion_comment']
            pk = request.POST['pk']

            # update comment
            FusionCheck.objects.filter(pk=request.POST['pk']).update(
                comment=request.POST['fusion_comment'],
                comment_updated=timezone.now(),
            )

            # TODO reload fusion data
                        # reload variant data
            context['fusion_data'] = get_fusion_info(sample_data, sample_obj)


        # if add new variant form is clicked
        if 'hgvs_g' in request.POST:
            new_variant_form = NewVariantForm(request.POST)

            if new_variant_form.is_valid():
                # TODO need to program function & make more robust

                #TODO- this needs more work -hardcoded values and table does not update automatically-page needs to be refreshed
                new_variant_data=new_variant_form.cleaned_data
                new_variant_object=Variant(genomic_37=new_variant_data.get("hgvs_g"), hgvs_p=new_variant_data.get("hgvs_p"))
                new_variant_object.save()
                new_variant_instance_object=VariantInstance(variant=new_variant_object, sample=sample_obj.sample, vaf=0, total_count=0, alt_count=0, in_ntc=False, manual_upload=True)
                new_variant_instance_object.save()
                new_variant_panel_object=VariantPanelAnalysis(variant_instance=new_variant_instance_object, sample_analysis=sample_obj)
                new_variant_panel_object.save()
                new_variant_check_object=VariantCheck(variant_analysis=new_variant_panel_object, check_object=sample_obj.get_checks().get("current_check_object"))
                new_variant_check_object.save()

                context['variant_data'] = get_variant_info(sample_data, sample_obj)




        # if finalise check submit form is clicked
        if 'next_step' in request.POST:
            submit_form = SubmitForm(request.POST)

            if submit_form.is_valid():
                if sample_data['sample_name'] == None:
                    context['warning'].append('Did not finalise check - input patient name before continuing')

                if (sample_data['dna_or_rna'] == 'DNA') and (current_step_obj.coverage_ntc_check == False):
                    context['warning'].append('Did not finalise check - check NTC before continuing')

                next_step = submit_form.cleaned_data['next_step']
                current_step = sample_data['checks']['current_status']

                if next_step == 'Complete check':

                    variants_match="yes"
                    variant_calls_dict=get_variant_info(sample_data, sample_obj)
                    variant_calls=variant_calls_dict.get('variant_calls')
                    for variant in variant_calls:
                        variant_data=variant.get('checks')
                        if (len(variant_data) >1):
                            last2=variant_data[-2:]
                            if last2[0]!=last2[1]:
                                variants_match="no"
                    if variants_match=="no":
                        context['warning'].append('Needs another check')

                else:
                    next_step = submit_form.cleaned_data['next_step']
                    current_step = sample_data['checks']['current_status']

                    if next_step == 'Complete check':
                        if 'IGV' in current_step:
                            # if 1st IGV, make 2nd IGV
                            if current_step == 'IGV check 1':
                                if signoff_check(request.user, current_step_obj, sample_obj):
                                    make_next_check(sample_obj, 'IGV')
                                    return redirect('view_samples', sample_data['worksheet_id'])
                                else:
                                    context['warning'].append('Did not finalise check - not all variant have been checked')
                                
                            # if 2nd IGV (or 3rd...) make interpretation
                            else:
                                if signoff_check(request.user, current_step_obj, sample_obj):
                                    return redirect('view_samples', sample_data['worksheet_id'])
                                else:
                                    context['warning'].append('Did not finalise check - not all variant have been checked')

                        # if interpretation, make complete
                        #elif 'Interpretation' in current_step:
                        #    if signoff_check(request.user, current_step_obj, sample_obj):
                        #        return redirect('view_samples', sample_data['worksheet_id'])
                        #    else:
                        #        context['warning'].append('Did not finalise check - not all variant have been checked')


                    elif next_step == 'Request extra check':
                        if 'IGV' in current_step:
                            # make extra IGV check
                            if signoff_check(request.user, current_step_obj, sample_obj):
                                make_next_check(sample_obj, 'IGV')
                                return redirect('view_samples', sample_data['worksheet_id'])
                            else:
                                context['warning'].append('Did not finalise check - not all variant have been checked')

                        # throw error, cant do this yet
                        #elif 'Interpretation' in current_step:
                        #    context['warning'].append("Only one interpretation check is carried out within this database, please only select eith 'Complete check' or 'Fail sample'")
                            # dont redirect - need to keep on current screen

                    elif next_step == 'Fail sample':
                        signoff_check(request.user, current_step_obj, sample_obj, 'F')
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
        #print(selections)

        if dna_or_rna == 'DNA':
            for variant in selections:
                variant_obj = VariantPanelAnalysis.objects.get(pk=variant)
                current_check = variant_obj.get_current_check()

                new_choice = selections[variant]['genuine_dropdown']
                current_check.decision = new_choice
                current_check.save()

                # TODO make more robust - could potentially end up with not analysed labelled as something else if people click multiple times
                if new_choice != 'N':
                    variant_instance_obj = variant_obj.variant_instance
                    variant_instance_obj.final_decision = new_choice
                    variant_instance_obj.save()

        elif dna_or_rna == 'RNA':
            for variant in selections:
                fusion_obj = FusionPanelAnalysis.objects.get(pk=variant)
                current_check = fusion_obj.get_current_check()

                new_choice = selections[variant]['genuine_dropdown']
                current_check.decision = new_choice
                current_check.save()

                # TODO make more robust - could potentially end up with not analysed labelled as something else if people click multiple times
                if new_choice != 'N':
                    fusion_obj = fusion_obj.fusion_instance
                    fusion_obj.final_decision = new_choice
                    fusion_obj.save()

        # dont think this redirect is doing anything but there needs to be a HTML response
        # actual reidrect is handled inside AJAX call in analysis-snvs.html
        return redirect('analysis_sheet', sample_pk)
