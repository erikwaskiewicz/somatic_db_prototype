from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import Field, FieldWithButtons, StrictButton


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


class PaperworkCheckForm(forms.Form):
    """
    Form that users tick after they have checked patient paperwork to confirm referral is correct
    """
    paperwork_check = forms.BooleanField(required=True, label='Confirm that paperwork is correct')
    sample = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(PaperworkCheckForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Continue to analysis', css_class='btn btn-info w-100')
        )


class NewVariantForm(forms.Form):
    """
    Manually add a SNV

    """
    hgvs_g = forms.CharField(label='Genomic coordinates')
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
        self.fields['hgvs_g'].widget.attrs['placeholder'] = 'e.g. 7:140453136A>T'
        self.fields['hgvs_c'].widget.attrs['placeholder'] = 'e.g. NM_004333.4:c.1799T>A'
        self.fields['hgvs_p'].widget.attrs['placeholder'] = 'e.g. NP_004324.2:p.(Val600Glu)'
        self.fields['gene'].widget.attrs['placeholder'] = 'e.g. BRAF'
        self.fields['exon'].widget.attrs['placeholder'] = 'e.g. 15 | 18 (for exon 15 of 18)'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-25')
        )


class SubmitForm(forms.Form):
    """
    Finalise a sample analysis

    """
    NEXT_STEP_CHOICES = (
        ('Complete check', 'Sample passed and check complete'),
        ('Request extra check', 'Sample passed, check complete but extra check required (dont do this at first check)'),
        ('Fail sample', 'Sample failed analysis but check is complete'),
    )
    next_step = forms.ChoiceField(choices=NEXT_STEP_CHOICES)
    confirm = forms.BooleanField(required=True, label='Confirm check is complete')

    def __init__(self, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-100')
        )


class SampleCommentForm(forms.Form):
    """
    Add a sample wide comment

    """
    sample_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label='General sample comments:'
    )
    patient_demographics = forms.BooleanField(required=False, label='Patient demographics checked')
    pk = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.comment = kwargs.pop('comment')
        self.info_check = kwargs.pop('info_check')
        self.pk = kwargs.pop('pk')

        super(SampleCommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['sample_comment'].initial = self.comment
        self.fields['patient_demographics'].initial = self.info_check
        self.fields['pk'].initial = self.pk
        self.helper.add_input(Submit('submit', 'Update', css_class='btn btn-success'))


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


class UpdatePatientName(forms.Form):
    """
    Add/ change the patient name

    """
    name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(UpdatePatientName, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['name'].widget.attrs.update({
            'autocomplete': 'off'
        })
        self.helper.form_id = 'update-name-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-25')
        )


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
        self.helper.add_input(Submit('submit', 'Update', css_class='btn btn-success'))


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
        self.fields['comment'].widget.attrs['placeholder'] = 'Add evidence to support this variant being a poly'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-100')
        )


class AddNewPolyForm(forms.Form):
    """
    Add a variant to the poly list

    """
    variant = forms.CharField()
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Comments'
    )

    def __init__(self, *args, **kwargs):
        super(AddNewPolyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['comment'].widget.attrs['placeholder'] = 'Add evidence to support this variant being a poly'
        self.fields['variant'].widget.attrs['placeholder'] = 'Must be in genomic format e.g. 7:140453136A>T'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-25')
        )
