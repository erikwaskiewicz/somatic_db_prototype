from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import Field, FieldWithButtons, StrictButton


class UnassignForm(forms.Form):
    """
    Search bar for home page
    """
    unassign = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(UnassignForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', "I'm sure", css_class='btn btn-danger w-100')
        )


class NewVariantForm(forms.Form):
    """
    """
    hgvs_g = forms.CharField(label='Genomic coordinates')
    hgvs_c = forms.CharField(label='HGVS c.')
    hgvs_p = forms.CharField(label='HGVS p.')
    gene = forms.CharField()
    exon = forms.CharField(required=False, label='Exon (in the format 1/5 for exon one of five.')
    alt_reads = forms.IntegerField()
    total_reads = forms.IntegerField()
    in_ntc = forms.BooleanField(required=False, label="Variant seen in NTC?")


    def __init__(self, *args, **kwargs):
        super(NewVariantForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'new-variant-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-25')
        )


class SubmitForm(forms.Form):
    """
    """
    NEXT_STEP_CHOICES = (
        ('Complete check', 'Complete check'),
        ('Request extra check', 'Request extra check'),
        ('Fail sample', 'Fail sample'),
    )
    next_step = forms.ChoiceField(choices=NEXT_STEP_CHOICES)
    confirm = forms.BooleanField(required=True, label="Confirm check is complete")


    def __init__(self, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-100')
        )


class SampleCommentForm(forms.Form):
    """
    """
    sample_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label='General sample comments:'
    )
    patient_demographics = forms.BooleanField(required=False, label="Patient demographics checked")
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

    """
    hgvs = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1}),
        required=False,
        label="HGVS"
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
    """
    ntc_checked = forms.BooleanField(required=False, label="NTC checked")
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
