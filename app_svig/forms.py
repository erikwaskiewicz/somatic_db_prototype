from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class NewClassification(forms.Form):
    """
    TODO remove this. just for adding a clean classification for testing

    """

    def __init__(self, *args, **kwargs):
        super(NewClassification, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'New', css_class='btn btn-info w-100')
        )


class CheckInfoForm(forms.Form):
    """
    Form that users tick to confirm they've checked the patient/variant info tab

    """
    check_info_form = forms.BooleanField(required=True, label="Confirm that the information on this page is correct")

    def __init__(self, *args, **kwargs):
        super(CheckInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Confirm', css_class='btn btn-warning w-100')
        )


class ResetCheckInfoForm(forms.Form):
    """
    Form to reset the check info form

    """
    reset_info_check = forms.BooleanField(required=True, label="Confirm that you want to reopen and that any analysis you've done so far will be wiped")

    def __init__(self, *args, **kwargs):
        super(ResetCheckInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Reopen', css_class='btn btn-danger w-100')
        )


class PreviousClassificationForm(forms.Form):
    """
    Choose whether to use a previous class of start a new one

    """
    PREVIOUS_CLASS_CHOICES = (
        (True, 'Use previous'),
        (False, 'New classification'),
    )
    use_previous_class = forms.ChoiceField(choices=PREVIOUS_CLASS_CHOICES)
    confirm_use_previous_class = forms.BooleanField(required=True, label='Confirm decision')

    def __init__(self, *args, **kwargs):
        super(PreviousClassificationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', "Submit", css_class='btn btn-warning w-100')
        )


class ResetPreviousClassificationsForm(forms.Form):
    """
    Form to reopen the previous classifications form

    """
    reset_previous_class_check = forms.BooleanField(required=True, label="Confirm that you want to reopen and that any S-VIG analysis you've done so far will be wiped")

    def __init__(self, *args, **kwargs):
        super(ResetPreviousClassificationsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Reopen', css_class='btn btn-danger w-100')
        )
