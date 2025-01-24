from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div
from crispy_forms.bootstrap import Field, FieldWithButtons, StrictButton, InlineCheckboxes
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from .models import Panel
import datetime

class UnassignForm(forms.Form):
    """
    Unassign yourself/ someone else from a sample analysis

    """
    unassign = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(UnassignForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', "I'm sure", css_class='btn btn-danger w-100')
        )


class ReopenSampleAnalysisForm(forms.Form):
    """
    Form that allows the user who closed the case to reopen the most recent check

    """
    reopen_analysis = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(ReopenSampleAnalysisForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', "I'm sure", css_class='btn btn-danger w-100')
        )


class PaperworkCheckForm(forms.Form):
    """
    Form that users tick after they have checked patient paperwork to confirm referral is correct

    """
    paperwork_check = forms.BooleanField(required=True, label='Confirm that paperwork is correct for the sample above')
    igv_check = forms.BooleanField(required=True, label='Confirm that IGV settings are correct for the assay above')
    sample = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(PaperworkCheckForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Continue to analysis', css_class='btn btn-info w-100')
        )


class RunQCForm(forms.Form):
    """
    Bioinformatics to perform QC on a worksheet

    """
    QC_CHOICES = (
        ('P', 'AutoQC run pass'),
        ('F', 'AutoQC run fail'),
    )
    qc_result = forms.ChoiceField(choices=QC_CHOICES, required=True, label='Whole run pass/fail, as performed in AutoQC')
    confirm = forms.BooleanField(required=True, label='All individual sample fails have been failed below')
    auto_qc_pk = forms.IntegerField(min_value=1, label='AutoQC primary key')

    def __init__(self, *args, **kwargs):
        super(RunQCForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Complete QC', css_class='btn btn-warning w-100')
        )


class ReopenRunQCForm(forms.Form):
    """
    Form that allows bioinformatics user to send a worksheet back to QC

    """
    reopen_qc = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(ReopenRunQCForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', "I'm sure", css_class='btn btn-danger w-100')
        )


class SampleQCForm(forms.Form):
    """
    Form for bioinformatics team to fail QC on an individual sample
    (no pass option as these sample will be left as they are ready for scientist to analyse)

    """
    fail_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=True,
        label='Reason for QC fail:'
    )
    confirm = forms.BooleanField(required=True, label="I confirm I want to fail this sample")

    def __init__(self, *args, **kwargs):
        super(SampleQCForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Fail sample', css_class='btn btn-danger w-100')
        )


class NewVariantForm(forms.Form):
    """
    Manually add a SNV. Splitting HGVS into components to stop formatting errors

    """
    chrm = forms.CharField(label='Chromosome')
    position = forms.IntegerField(label='Genomic coordinates')
    ref = forms.CharField(label='Reference nucleotide')
    alt = forms.CharField(label='Alt nucleotide')
    hgvs_c = forms.CharField(label='HGVS c.')
    hgvs_p = forms.CharField(label='HGVS p.')
    gene = forms.CharField()
    exon = forms.CharField(required=False, label='Exon')
    alt_reads = forms.IntegerField(label='Number of reads supporting variant')
    total_reads = forms.IntegerField(label='Total depth')
    in_ntc = forms.BooleanField(required=False, label='Variant seen in NTC?')

    def __init__(self, *args, **kwargs):
        super(NewVariantForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'new-variant-form'
        self.fields['chrm'].widget.attrs['placeholder'] = 'e.g. 7'
        self.fields['position'].widget.attrs['placeholder'] = 'e.g. 140453136'
        self.fields['ref'].widget.attrs['placeholder'] = 'e.g. A'
        self.fields['alt'].widget.attrs['placeholder'] = 'e.g. T'
        self.fields['hgvs_c'].widget.attrs['placeholder'] = 'e.g. NM_004333.4:c.1799T>A'
        self.fields['hgvs_p'].widget.attrs['placeholder'] = 'e.g. NP_004324.2:p.(Val600Glu)'
        self.fields['gene'].widget.attrs['placeholder'] = 'e.g. BRAF'
        self.fields['exon'].widget.attrs['placeholder'] = 'e.g. 15 | 18 (for exon 15 of 18)'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-25')
        )


class NewFusionForm(forms.Form):
    """
    Manually add a fusion

    """
    fusion_genes = forms.CharField(label='Fusion')
    hgvs = forms.CharField(label='HGVS', required=False)
    fusion_supporting_reads = forms.IntegerField(label='Number of reads supporting the fusion')
    ref_reads_1 = forms.IntegerField(label='Number of reference reads (only needed for ctDNA)', required=False)
    left_breakpoint = forms.CharField(label='Left breakpoint')
    right_breakpoint = forms.CharField(label='Right breakpoint')
    in_ntc = forms.BooleanField(required=False, label='Variant seen in NTC?')

    def __init__(self, *args, **kwargs):
        super(NewFusionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'new-fusion-form'
        self.fields['fusion_genes'].widget.attrs['placeholder'] = 'e.g. EML4-ALK'
        self.fields['left_breakpoint'].widget.attrs['placeholder'] = 'e.g. chr2:234567'
        self.fields['right_breakpoint'].widget.attrs['placeholder'] = 'e.g. chr2:4567890'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-25')
        )


class SubmitForm(forms.Form):
    """
    Form for scientists to finalise a sample analysis.
    Gives an analysis pass/fail option and the option of whether or not to send for an additional check
    Options are disabled in the GUI by some AJAX calls based on the status of the sample

    """
    PASS_FAIL_CHOICES = (
        ('C', 'Analysis pass'),
        ('F', 'Analysis fail')
    )
    NEXT_STEP_CHOICES = (
        ('extra_check', 'Send for an extra check'),
        ('finalise', 'Close analysis for this sample'),
    )
    analysis_pass_fail = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=PASS_FAIL_CHOICES, label='Has the sample analysis passed?')
    next_step = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=NEXT_STEP_CHOICES)
    confirm = forms.BooleanField(required=True, label='Confirm selections are correct')


class SendCheckBackForm(forms.Form):
    """
    Form to send a check back the the previous checker, will delete current check

    """
    send_back_check = forms.BooleanField(required=True, label='I understand that my check will be removed')
    inform_user_check = forms.BooleanField(required=True, label="I have notified the user that I'm sending this check back to them")

    def __init__(self, *args, **kwargs):
        super(SendCheckBackForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Confirm', css_class='btn btn-danger w-100')
        )


class DetailsCheckForm(forms.Form):
    """
    Form for scientists to confirm that they've checked all the patient demographics

    """
    patient_demographics = forms.BooleanField(required=True, label='Patient demographics are correct')

    def __init__(self, *args, **kwargs):
        self.info_check = kwargs.pop('info_check')

        super(DetailsCheckForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['patient_demographics'].initial = self.info_check
        self.helper.add_input(Submit('submit', 'Update', css_class='btn btn-warning'))


class SampleCommentForm(forms.Form):
    """
    Add a sample wide comment

    """
    sample_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label='General sample comments:'
    )
    pk = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.comment = kwargs.pop('comment')
        self.pk = kwargs.pop('pk')

        super(SampleCommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['sample_comment'].initial = self.comment
        self.fields['pk'].initial = self.pk
        self.helper.add_input(Submit('submit', 'Update', css_class='btn btn-warning'))


class VariantCommentForm(forms.Form):
    """
    Add a comment to a specific SNV

    """
    variant_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
    )
    pk = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):

        self.comment = kwargs.pop('comment')
        self.pk = kwargs.pop('pk')

        super(VariantCommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['variant_comment'].initial = self.comment
        self.fields['pk'].initial = self.pk
        self.helper.add_input(Submit('submit', 'Update', css_class='btn btn-success'))


class FusionCommentForm(forms.Form):
    """
    Add a comment to a specific fusion

    """
    hgvs = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1}),
        required=False,
        label='HGVS'
    )
    fusion_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
    )
    pk = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):

        self.comment = kwargs.pop('comment')
        self.hgvs = kwargs.pop('hgvs')
        self.pk = kwargs.pop('pk')

        super(FusionCommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['fusion_comment'].initial = self.comment
        self.fields['hgvs'].initial = self.hgvs
        self.fields['pk'].initial = self.pk
        self.helper.add_input(Submit('submit', 'Update', css_class='btn btn-success'))


class CoverageCheckForm(forms.Form):
    """
    Confirm that coverage has been checked and add a comment 

    """
    ntc_checked = forms.BooleanField(required=False, label='NTC checked')
    coverage_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    pk = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):

        self.comment = kwargs.pop('comment')
        self.ntc = kwargs.pop('ntc_check')
        self.pk = kwargs.pop('pk')

        super(CoverageCheckForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['coverage_comment'].initial = self.comment
        self.fields['ntc_checked'].initial = self.ntc
        self.fields['pk'].initial = self.pk
        self.helper.add_input(Submit('submit', 'Update', css_class='btn btn-warning'))


class ManualVariantCheckForm(forms.Form):
    """
    Confirm that a manual review of IGV for specific variants has been completed

    """
    # hidden field to identify form within view
    variants_checked = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):

        # make regions passed in as list
        self.regions = kwargs.pop('regions')

        super(ManualVariantCheckForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout()

        # loop through regions and make a checkbox for each
        for r in self.regions:
            self.fields[r] = forms.BooleanField(required=True, label=r)

        self.helper.add_input(Submit('submit', 'Complete manual check', css_class='btn btn-secondary'))


class ConfirmPolyForm(forms.Form):
    """
    Confirm that a variant should be added to the poly list

    """
    confirm = forms.BooleanField(required=True, label='I agree that this variant is a poly')
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Comments'
    )
    variant_pk = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(ConfirmPolyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['comment'].widget.attrs['placeholder'] = 'Add comments or evidence to support this variant being a poly\ne.g. filepaths to documented evidence, sample IDs to check...'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-100')
        )


class ConfirmArtefactForm(forms.Form):
    """
    Confirm that a variant should be added to the artefact list

    """
    confirm = forms.BooleanField(required=True, label='I agree that this variant is an artefact')
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Comments'
    )
    variant_pk = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(ConfirmArtefactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['comment'].help_text = 'Add comments or evidence to support this variant being a artefact\ne.g. filepaths to documented evidence, sample IDs to check...'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-100')
        )


class AddNewPolyForm(forms.Form):
    """
    Add a variant to the poly list

    """
    chrm = forms.CharField(label='Chromosome')
    position = forms.IntegerField(label='Genomic coordinates')
    ref = forms.CharField(label='Reference nucleotide')
    alt = forms.CharField(label='Alt nucleotide')
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Comments'
    )

    def __init__(self, *args, **kwargs):
        super(AddNewPolyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['chrm'].widget.attrs['placeholder'] = 'e.g. 7'
        self.fields['position'].widget.attrs['placeholder'] = 'e.g. 140453136'
        self.fields['ref'].widget.attrs['placeholder'] = 'e.g. A'
        self.fields['alt'].widget.attrs['placeholder'] = 'e.g. T'
        self.fields['comment'].widget.attrs['placeholder'] = 'Add comments or evidence to support this variant being a poly\ne.g. filepaths to documented evidence, sample IDs to check...'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-25')
        )

       
class AddNewArtefactForm(forms.Form):
    """
    Add a variant to the artefact list

    """
    chrm = forms.CharField(label='Chromosome')
    position = forms.IntegerField(label='Genomic coordinates')
    ref = forms.CharField(label='Reference nucleotide')
    alt = forms.CharField(label='Alt nucleotide')
    vaf_cutoff = forms.DecimalField(label='VAF cutoff', min_value=0, max_value=100, decimal_places=5)
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Comments'
    )

    def __init__(self, *args, **kwargs):
        super(AddNewArtefactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['chrm'].widget.attrs['placeholder'] = 'e.g. 7'
        self.fields['position'].widget.attrs['placeholder'] = 'e.g. 140453136'
        self.fields['ref'].widget.attrs['placeholder'] = 'e.g. A'
        self.fields['alt'].widget.attrs['placeholder'] = 'e.g. T'
        self.fields['vaf_cutoff'].initial = 0.0
        self.fields['vaf_cutoff'].widget.attrs['placeholder'] = 'Only variants below this value will be filtered as artefacts. If no cutoff is required then leave as 0.'
        self.fields['comment'].widget.attrs['placeholder'] = 'Add comments or evidence to support this variant being an artefact\ne.g. filepaths to documented evidence, sample IDs to check...'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-25')
        )


class AddNewFusionArtefactForm(forms.Form):
    """
    Add a fusion to the artefact list

    """
    left_breakpoint = forms.CharField()
    right_breakpoint = forms.CharField()
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Comments'
    )

    def __init__(self,*args,**kwargs):
        super(AddNewFusionArtefactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['comment'].help_text = 'Add comments or evidence to support this fusion being an artefact\ne.g. filepaths to documented evidence, sample IDs to check...'
        self.fields['left_breakpoint'].help_text = 'Must be in genomic format e.g. chr1:123456'
        self.fields['right_breakpoint'].help_text = 'Must be in genomic format e.g. chr2:789012'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-25')
        )


class ChangeLimsInitials(forms.Form):
    """
    Add/ change the user initials as displayed in LIMS

    """
    lims_initials = forms.CharField(label='LIMS initials', max_length=10)

    def __init__(self, *args, **kwargs):
        super(ChangeLimsInitials, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'lims-initials-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-25')
        )


class EditedPasswordChangeForm(PasswordChangeForm):
    """
    Add a submit button to the base password change form

    """
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'password-change-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Change password', css_class='btn btn-danger w-100')
        )


class EditedUserCreationForm(UserCreationForm):
    """
    Add LIMS initials to the base user creation form

    """
    lims_initials = forms.CharField(label='LIMS initials')

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['lims_initials'].help_text = 'Input initials as displayed in LIMS, this must match for integration between SVD and LIMS. If unsure then input as ?, it can be edited within user settings in future.'
        self.helper.form_id = 'signup-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-100')
        )

class SelfAuditSubmission(forms.Form):
    """
    Choose Assay and date range for self audit view

    """
    # Starting parameters for the dropdowns
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    current_day = datetime.datetime.now().day
    last_year = current_year - 1

    # Setting range for year choice
    year_choices = range(2019, (current_year + 1))
    
    # Default to present day and 1 year ago
    initial_start_date = datetime.datetime(last_year, current_month, current_day)
    initial_end_date = datetime.datetime.now()
    
    start_date = forms.DateField(
        initial = initial_start_date,
         widget = forms.SelectDateWidget(years = year_choices,attrs={
            'style': 'width: 150px',
        }
        )
    )
    end_date = forms.DateField(
        initial = initial_end_date,
        widget = forms.SelectDateWidget(years = year_choices,attrs={
            'style': 'width: 150px',
        }
        )
    )

    which_assays = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
     choices=Panel.ASSAY_CHOICES,
     required=True,
    )
    
    # Radioselect for submission
    submit_check = forms.ChoiceField(widget=forms.RadioSelect,
     choices=[('1', 'I have selected the dates and assays')]
     )
    
    def __init__(self, *args, **kwargs):
        super(SelfAuditSubmission, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Field('start_date', css_class='form-control', wrapper_class='col-md-4'),
                Field('end_date', css_class='form-control', wrapper_class='col-md-4'),
                css_class='row'
            ),
            InlineCheckboxes('which_assays'),
            Field('submit_check')
            )
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('display_submit', 'Search', css_class='btn btn-info')  
        )
        self.helper.add_input(
            Submit('download_submit', 'Download', css_class='btn btn-success')
        )
