from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.template.loader import get_template
from django.template import Context


from .forms import NewVariantForm, SubmitForm, VariantCommentForm, UpdatePatientName, CoverageCheckForm, FusionCommentForm, SampleCommentForm, UnassignForm, PaperworkCheckForm, ConfirmPolyForm, AddNewPolyForm
from .models import *
from .utils import link_callback, get_samples, unassign_check, signoff_check, make_next_check, get_variant_info, get_coverage_data, get_sample_info, get_fusion_info, create_myeloid_coverage_summary, get_poly_list


import json
import os

from xhtml2pdf import pisa 
    

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
            user.is_active = False
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
    return redirect('view_worksheets', 'recent')


@login_required
def view_worksheets(request, query):
    """
    Displays all worksheets and links to the page to show all samples 
    within the worksheet
    """
    # based on URL, either query 30 most recent or all results
    if query == 'recent':
        worksheets = Worksheet.objects.filter(diagnostic=True).order_by('-run')[:30]
        filtered = True

    elif query == 'all':
        worksheets = Worksheet.objects.all().order_by('-run')
        filtered = False

    # any other string will be chnaged to most recent, if left blank then it'll throw a 404 error
    else:
        return redirect('view_worksheets', 'recent')


    # Two seperate lists so that diagnostics runs appear first
    diagnostics_ws_list = []
    other_ws_list = []

    for w in worksheets:
        # if first two characters are digits, add to diagnostics list, otherwise add to other list
        if w.diagnostic:
            diagnostics_ws_list.append({
                'worksheet_id': w.ws_id,
                'run_id': w.run.run_id,
                'assay': w.assay,
                'status': w.get_status(),
            })
        else:
            other_ws_list.append({
                'worksheet_id': w.ws_id,
                'run_id': w.run.run_id,
                'assay': w.assay,
                'status': w.get_status(),
            })

    ws_list = diagnostics_ws_list + other_ws_list

    context = {
        'worksheets': ws_list,
        'filtered': filtered,
    }

    return render(request, 'analysis/view_worksheets.html', context)


@login_required
def view_samples(request, worksheet_id):
    """
    Displays all samples with a worksheet and links to the analysis 
    for the sample
    """
    samples = SampleAnalysis.objects.filter(worksheet = worksheet_id)
    sample_dict = get_samples(samples)
    ws_obj = Worksheet.objects.get(ws_id = worksheet_id)
    run_id = ws_obj.run

    if request.method == 'POST':
        # if unassign modal button is pressed
        if 'unassign' in request.POST:
            unassign_form = UnassignForm(request.POST)
            if unassign_form.is_valid():
                # get sample analysis pk from form
                sample_pk = unassign_form.cleaned_data['unassign']
                sample_analysis_obj = SampleAnalysis.objects.get(pk=sample_pk)

                # get latest check and reset
                unassign_check(sample_analysis_obj)

                # redirect to force refresh, otherwise form could accidentally be resubmitted when refreshing the page
                return redirect('view_samples', worksheet_id)

        # if someone starts a first check
        if 'paperwork_check' in request.POST:
            check_form = PaperworkCheckForm(request.POST)
            if check_form.is_valid():
                # get sample analysis pk from form
                sample_pk = check_form.cleaned_data['sample']
                sample_analysis_obj = SampleAnalysis.objects.get(pk=sample_pk)

                # set the check to true and redirect to the sample
                sample_analysis_obj.paperwork_check = True
                sample_analysis_obj.save()

                return redirect('analysis_sheet', sample_analysis_obj.pk)

    # render context
    context = {
        'worksheet': worksheet_id,
        'run_id': run_id,
        'samples': sample_dict,
        'unassign_form': UnassignForm(),
        'check_form': PaperworkCheckForm(),
    }

    return render(request, 'analysis/view_samples.html', context)


@login_required
def analysis_sheet(request, sample_id):
    """
    Display coverage and variant metrics to allow checking of data 
    in IGV
    """
    # load sample object, error if the paperwork check hasnt been done
    sample_obj = SampleAnalysis.objects.get(pk = sample_id)
    if sample_obj.paperwork_check == False:
        raise Http404("Paperwork hasn't been checked")

    # load in data that is common to both RNA and DNA workflows
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
        'sample_comment_form': SampleCommentForm(
            comment=current_step_obj.overall_comment,
            info_check=current_step_obj.patient_info_check,
            pk=current_step_obj.pk, 
        ),
        'coverage_check_form': CoverageCheckForm(
            pk=current_step_obj.pk, 
            comment=current_step_obj.coverage_comment,
            ntc_check=current_step_obj.coverage_ntc_check,
        ),
    }

    # pull out coverage summary for myeloid, otherwise return false
    if sample_data['is_myeloid_referral']:
        myeloid_coverage_summary = create_myeloid_coverage_summary(sample_obj)
    else:
        myeloid_coverage_summary = False

    # DNA workflow
    if sample_data['panel_obj'].show_snvs == True:
        context['variant_data'] = get_variant_info(sample_data, sample_obj)
        context['coverage_data'] = get_coverage_data(sample_obj)
        context['myeloid_coverage_summary'] = myeloid_coverage_summary

    # RNA workflow
    elif sample_data['panel_obj'].show_fusions == True:
        context['fusion_data'] = get_fusion_info(sample_data, sample_obj)

        
    ####################################
    #  If any buttons are pressed
    ####################################

    # download PDF reports
    if request.method == 'GET':

        if 'download-dna' in request.GET:
            filename=f"{context['sample_data']['worksheet_id']}_{context['sample_data']['sample_id']}_{context['sample_data']['panel']}.pdf"

            # Create a Django response object, and specify content_type as pdf
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            # find the template and render it.
            template = get_template('analysis/download_dna_report.html')
            html = template.render(context)

            # create a pdf
            pisa_status = pisa.CreatePDF(
                html, dest=response, link_callback=link_callback
            )

            return response

    # submit buttons
    if request.method == 'POST':
        # patient name input form
        if 'name' in request.POST:
            update_name_form = UpdatePatientName(request.POST)

            if update_name_form.is_valid():
                new_name = update_name_form.cleaned_data['name']
                Sample.objects.filter(pk=sample_obj.sample.pk).update(sample_name=new_name)
                sample_obj = SampleAnalysis.objects.get(pk = sample_id)
                context['sample_data'] = get_sample_info(sample_obj)

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
            hgvs = request.POST['hgvs']
            pk = request.POST['pk']

            # update comment
            fusion_check_obj = FusionCheck.objects.get(pk=request.POST['pk'])
            fusion_check_obj.comment=request.POST['fusion_comment']
            fusion_check_obj.comment_updated=timezone.now()

            # update fusion HGVS
            fusion_instance = fusion_check_obj.fusion_analysis.fusion_instance
            fusion_instance.hgvs = hgvs

            # save objects to database
            fusion_check_obj.save()
            fusion_instance.save()
            
            # reload variant data
            context['fusion_data'] = get_fusion_info(sample_data, sample_obj)


        # if add new variant form is clicked
        if 'hgvs_g' in request.POST:
            new_variant_form = NewVariantForm(request.POST)

            if new_variant_form.is_valid():

                new_variant_data = new_variant_form.cleaned_data
		
                #Error out if total depth is set to zero
                if new_variant_data['total_reads'] == 0:
                                	
                    context['warning'].append('Total read counts can not be zero')
                    
                elif new_variant_data['alt_reads'] == 0:
                
                     context['warning'].append('Alt read counts can not be zero')
                    
                else:
                
                    #Lock to same genome build as sample_analysis 
                    new_variant_object, created = Variant.objects.get_or_create(
                        variant = new_variant_data['hgvs_g'],
                        genome_build = sample_obj.genome_build,

                    )
                    new_variant_object.save()
                    new_variant_instance_object = VariantInstance(
                        variant = new_variant_object,
                        gene = new_variant_data['gene'],
                        exon = new_variant_data['exon'],
                        hgvs_c = new_variant_data['hgvs_c'],
                        hgvs_p = new_variant_data['hgvs_p'],
                        sample = sample_obj.sample, 
                        total_count = new_variant_data['total_reads'], 
                        alt_count = new_variant_data['alt_reads'], 
                        in_ntc = new_variant_data['in_ntc'], 
                        manual_upload = True,
                    )
                    new_variant_instance_object.save()
                    new_variant_panel_object = VariantPanelAnalysis(
                        variant_instance=new_variant_instance_object, 
                        sample_analysis=sample_obj
                    )
                    new_variant_panel_object.save()
                    new_variant_check_object = VariantCheck(
                        variant_analysis=new_variant_panel_object, 
                        check_object=sample_obj.get_checks().get('current_check_object')
                    )
                    new_variant_check_object.save()

                    # reload context
                    context['variant_data'] = get_variant_info(sample_data, sample_obj)


        # overall sample comments form
        if 'sample_comment' in request.POST:
            new_comment = request.POST['sample_comment']
            try:
                if request.POST['patient_demographics'] == 'on':
                    info_check = True
            except:
                info_check = False
            pk = request.POST['pk']

            # update comment
            Check.objects.filter(pk=pk).update(
                overall_comment=new_comment,
                overall_comment_updated=timezone.now(),
                patient_info_check=info_check,
            )

            # reload sample data
            context['sample_data'] = get_sample_info(sample_obj)
            current_step_obj = context['sample_data']['checks']['current_check_object']
            context['sample_comment_form'] = SampleCommentForm(
                comment=current_step_obj.overall_comment,
                info_check=current_step_obj.patient_info_check,
                pk=current_step_obj.pk, 
            )



        # if finalise check submit form is clicked
        if 'next_step' in request.POST:
            submit_form = SubmitForm(request.POST)

            if submit_form.is_valid():
                next_step = submit_form.cleaned_data['next_step']
                current_step = sample_data['checks']['current_status']
                
                if sample_data['sample_name'] == None:
                    context['warning'].append('Did not finalise check - input patient name before continuing')

                if (sample_data['panel_obj'].show_snvs == True) and (current_step_obj.coverage_ntc_check == False) and (next_step != "Fail sample"):
                    context['warning'].append('Did not finalise check - check NTC before continuing')

                if current_step_obj.patient_info_check == False:
                    context['warning'].append('Did not finalise check - check patient demographics before continuing')

                # only enter this loop if there are no warnings so far, otherwise the warnings above get skipped
                if len(context['warning']) == 0:
                    if next_step == 'Complete check':

                        # if 1st IGV, make 2nd IGV
                        if current_step == 'IGV check 1':
                            submitted, err = signoff_check(request.user, current_step_obj, sample_obj)
                            if submitted:
                                make_next_check(sample_obj, 'IGV')
                                return redirect('view_samples', sample_data['worksheet_id'])
                            else:
                                context['warning'].append(err)
                            
                        # if 2nd IGV (or 3rd...)
                        else:
                            # Check whether the last two checkers disagree
                            variants_match = True
                            non_matching_variants = []

                            # TODO - replace with true/flase, same below
                            if sample_data['panel_obj'].show_snvs == True:
                                for variant in context['variant_data']['variant_calls']:
                                    if not variant['latest_checks_agree']:
                                        variants_match = False
                                        non_matching_variants.append(variant['genomic'])

                            if sample_data['panel_obj'].show_fusions == True:
                                for fusion in context['fusion_data']['fusion_calls']:
                                    if not fusion['latest_checks_agree']:
                                        variants_match = False
                                        non_matching_variants.append(fusion['fusion_genes'])

                            if not variants_match:
                                warning_text = ', '.join(non_matching_variants)
                                context['warning'].append(f'Did not finalise check - the last two checkers dont agree for the following variants: {warning_text}')
                            
                            # final signoff
                            else:
                                submitted, err = signoff_check(request.user, current_step_obj, sample_obj, complete=True)
                                if submitted:
                                    return redirect('view_samples', sample_data['worksheet_id'])

                                # throw warning if not all variants are checked
                                else:
                                    context['warning'].append(err)

                    elif next_step == 'Request extra check':

                        # make extra IGV check
                        submitted, err = signoff_check(request.user, current_step_obj, sample_obj)
                        if submitted:
                            make_next_check(sample_obj, 'IGV')
                            return redirect('view_samples', sample_data['worksheet_id'])
                        else:
                            context['warning'].append(err)


                    elif next_step == 'Fail sample':

                        # TODO other checks on fails??? - will only count total fails, not two in a row/ mixture of fails and passes

                        # if failed 1st check, make 2nd check 
                        if current_step == 'IGV check 1':
                            signoff_check(request.user, current_step_obj, sample_obj, status='F')
                            make_next_check(sample_obj, 'IGV')
                            return redirect('view_samples', sample_data['worksheet_id'])

                        # otherwise sign off and make sample failed
                        else:
                            signoff_check(request.user, current_step_obj, sample_obj, status='F')
                            return redirect('view_samples', sample_data['worksheet_id'])


    # render the pages
    return render(request, 'analysis/analysis_sheet.html', context)


def ajax(request):
    """
    Handles the submission of the genuine/ artefact etc dropdown box
    """
    if request.is_ajax():

        sample_pk = request.POST.get('sample_pk')
        sample_obj = SampleAnalysis.objects.get(pk = sample_pk)
        dna_or_rna = sample_obj.sample.sample_type

        selections = json.loads(request.POST.get('selections'))

        if dna_or_rna == 'DNA':
            for variant in selections:
                variant_obj = VariantPanelAnalysis.objects.get(pk=variant)
                current_check = variant_obj.get_current_check()

                new_choice = selections[variant]['genuine_dropdown']
                current_check.decision = new_choice
                current_check.save()

        elif dna_or_rna == 'RNA':
            for variant in selections:
                fusion_obj = FusionPanelAnalysis.objects.get(pk=variant)
                current_check = fusion_obj.get_current_check()

                new_choice = selections[variant]['genuine_dropdown']
                current_check.decision = new_choice
                current_check.save()

        # dont think this redirect is doing anything but there needs to be a HTML response
        # actual reidrect is handled inside AJAX call in analysis-snvs.html
        return redirect('analysis_sheet', sample_pk)


@login_required
def view_polys(request):
    """
    Page to view all confirmed polys and add and check new ones

    """
    #Get all poly lists
    poly_list = VariantList.objects.filter(list_type='P')

    # pull out list of confirmed polys and polys to be checked - this will initially make a list of lists - then convert into a single list! 
    confirmed_list = []
    checking_list = []

    for i in poly_list:
        
        temp_confirmed_list, temp_checking_list = get_poly_list(i, request.user)
        confirmed_list.append(temp_confirmed_list)
        checking_list.append(temp_checking_list)
    
    #Flatten the list of lists    
    confirmed_list_final = [item for sublist in confirmed_list for item in sublist]
    checking_list_final = [item for sublist in checking_list for item in sublist]

    # make context dictionary
    context = {
        'success': [],
        'warning': [],
        'confirmed_list': confirmed_list_final,
        'checking_list': checking_list_final,
        'confirm_form': ConfirmPolyForm(),
        'add_new_form': AddNewPolyForm(),
    }

    #----------------------------------------------------------
    #  If any buttons are pressed
    if request.method == 'POST':

        # if confirm poly button is pressed
        if 'variant_pk' in request.POST:

            confirm_form = ConfirmPolyForm(request.POST)
            if confirm_form.is_valid():

                # get form data
                variant_pk = confirm_form.cleaned_data['variant_pk']
                comment = confirm_form.cleaned_data['comment']

                # update poly list
                variant_to_variant_list_obj = VariantToVariantList.objects.get(pk=variant_pk)
                variant_to_variant_list_obj.check_user = request.user
                variant_to_variant_list_obj.check_time = timezone.now()
                variant_to_variant_list_obj.check_comment = comment
                variant_to_variant_list_obj.save()

                # get genomic coords
                variant_obj = variant_to_variant_list_obj.variant
                variant = variant_obj.variant

                # reload context
                #Get all poly lists
                poly_list = VariantList.objects.filter(list_type='P')

                # pull out list of confirmed polys and polys to be checked - this will initially make a list of lists - then convert into a single list! 
                confirmed_list = []
                checking_list = []

                for i in poly_list:
        
                    temp_confirmed_list, temp_checking_list = get_poly_list(i, request.user)
                    confirmed_list.append(temp_confirmed_list)
                    checking_list.append(temp_checking_list)
    
                #Flatten the list of lists    
                confirmed_list_final = [item for sublist in confirmed_list for item in sublist]
                checking_list_final = [item for sublist in checking_list for item in sublist]
                
                context['confirmed_list'] = confirmed_list_final
                context['checking_list'] = checking_list_final
                context['success'].append(f'Variant {variant} added to poly list')

        # if add new poly button is pressed
        if 'variant' in request.POST:
            add_new_form = AddNewPolyForm(request.POST)

            if add_new_form.is_valid():

                # get form data
                variant = add_new_form.cleaned_data['variant']
                comment = add_new_form.cleaned_data['comment']
                genome = add_new_form.cleaned_data['genome']
            
                # wrap in try/ except to handle when a variant doesnt match the input
                try:
                    # load in variant and variant to list objects
                    variant_obj = Variant.objects.get(variant=variant, genome_build=genome)
                   
                    if genome == '37':
                        poly_list = VariantList.objects.get(name='build_37_polys')
      
                    elif genome == '38':
                        poly_list = VariantList.objects.get(name='build_38_polys')
                        
                    variant_to_variant_list_obj, created = VariantToVariantList.objects.get_or_create(
                        variant_list = poly_list,
                        variant = variant_obj,
                    )

                    # add user info if a new model is created
                    if created:
                        variant_to_variant_list_obj.upload_user = request.user
                        variant_to_variant_list_obj.upload_time = timezone.now()
                        variant_to_variant_list_obj.upload_comment = comment
                        variant_to_variant_list_obj.save()

                        # give success message
                        context['success'].append(f'Variant {variant} added to poly checking list')

                    # throw error if already in poly list
                    else:
                        context['warning'].append(f'Variant {variant} is already in the poly list')

                    # reload context
                    #Get all poly lists
                    poly_list = VariantList.objects.filter(list_type='P')

                    # pull out list of confirmed polys and polys to be checked - this will initially make a list of lists - then convert into a single list! 
                    confirmed_list = []
                    checking_list = []
 
                    for i in poly_list:
        
                        temp_confirmed_list, temp_checking_list = get_poly_list(i, request.user)
                        confirmed_list.append(temp_confirmed_list)
                        checking_list.append(temp_checking_list)
    
                    #Flatten the list of lists    
                    confirmed_list_final = [item for sublist in confirmed_list for item in sublist]
                    checking_list_final = [item for sublist in checking_list for item in sublist]
        
                    context['confirmed_list'] = confirmed_list_final
                    context['checking_list'] = checking_list_final

                # throw error if there isnt a variant matching the input
                except Variant.DoesNotExist:
                    context['warning'].append(f'Cannot find variant matching {variant}') 

    # render the page
    return render(request, 'analysis/view_polys.html', context)
