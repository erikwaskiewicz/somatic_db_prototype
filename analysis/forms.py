from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import Field, FieldWithButtons, StrictButton


class SearchForm(forms.Form):
    """
    Search bar for home page
    """
    search_text = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'search-form'
        self.helper.form_show_labels = False
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            FieldWithButtons(
                Field(
                    'search_text', 
                    placeholder='Start typing a sample or worksheet ID...'
                ), 
                StrictButton(
                    '<span class="fa fa-search"></span>', 
                    css_class='btn-secondary', 
                    type='submit', 
                    name='home-search-form'
                )
            )
        )


class NewVariantForm(forms.Form):
    """
    """
    hgvs_g = forms.CharField()
    hgvs_p = forms.CharField()

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
    confirm = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-100')
        )


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
    fusion_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
    )
    pk = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):

        self.comment = kwargs.pop('comment')
        self.pk = kwargs.pop('pk')

        super(FusionCommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['fusion_comment'].initial = self.comment
        self.fields['pk'].initial = self.pk
        self.helper.add_input(Submit('submit', 'Update', css_class='btn btn-success'))


class UpdatePatientName(forms.Form):
    """
    """
    name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(UpdatePatientName, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'update-name-form'
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn btn-info w-25')
        )



class CheckPatientName(forms.Form):
    """
    """
    name_checked = forms.BooleanField(required=True)
    checker_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    def __init__(self, *args, **kwargs):

        super(CheckPatientName, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Update', css_class='btn btn-success'))

class CoverageCheckForm(forms.Form):
    """
    """
    ntc_checked = forms.BooleanField(required=True, label="NTC checked")
    coverage_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    def __init__(self, *args, **kwargs):

        self.comment = kwargs.pop('comment')

        super(CoverageCheckForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['coverage_comment'].initial = self.comment
        self.helper.add_input(Submit('submit', 'Update', css_class='btn btn-success'))
