from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from somatic_variant_db.settings import BIOLOGICAL_CLASS_CHOICES, CLINICAL_CLASS_CHOICES


class NewClassification(forms.Form):
    """
    TODO remove this. just for adding a clean classification for testing

    """

    def __init__(self, *args, **kwargs):
        super(NewClassification, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "New", css_class="btn btn-info w-100"))


class CheckInfoForm(forms.Form):
    """
    Form that users tick to confirm they've checked the patient/variant info tab

    """

    check_info_form = forms.BooleanField(
        required=True, label="Confirm that the information on this page is correct"
    )

    def __init__(self, *args, **kwargs):
        super(CheckInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Confirm", css_class="btn btn-info w-100")
        )


class ReopenCheckInfoForm(forms.Form):
    """
    Form to reset the check info form

    """

    reset_info_check = forms.BooleanField(
        required=True,
        label="Confirm that you want to reopen and that any analysis you've done so far will be wiped",
    )

    def __init__(self, *args, **kwargs):
        super(ReopenCheckInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Reopen", css_class="btn btn-danger w-100")
        )


class PreviousClassificationForm(forms.Form):
    """
    Choose whether to use a previous class of start a new one

    """

    use_previous_class = forms.ChoiceField(label="Choose next step")
    confirm_use_previous_class = forms.BooleanField(
        required=True, label="Confirm decision"
    )

    def __init__(self, *args, **kwargs):
        self.previous_class_choices = kwargs.pop("previous_class_choices")

        super(PreviousClassificationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.fields["use_previous_class"].choices = self.previous_class_choices
        self.helper.add_input(
            Submit("submit", "Submit", css_class="btn btn-info w-100")
        )


class ReopenPreviousClassificationsForm(forms.Form):
    """
    Form to reopen the previous classifications form

    """

    reset_previous_class_check = forms.BooleanField(
        required=True,
        label="Confirm that you want to reopen and that any interpretation you've done so far will be wiped",
    )

    def __init__(self, *args, **kwargs):
        super(ReopenPreviousClassificationsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Reopen", css_class="btn btn-danger w-100")
        )


class CompleteSvigForm(forms.Form):
    """
    Form to complete the SVIG tab

    """

    CLASS_CHOICES = (("No", "No override"),) + BIOLOGICAL_CLASS_CHOICES

    override = forms.ChoiceField(choices=CLASS_CHOICES)
    complete_svig = forms.BooleanField(
        required=True, label="Confirm analysis is complete"
    )

    def __init__(self, *args, **kwargs):
        super(CompleteSvigForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Complete", css_class="btn btn-info w-100")
        )


class ReopenSvigForm(forms.Form):
    """
    Form to reopen the previous classifications form

    """

    reset_svig_check = forms.BooleanField(
        required=True, label="Confirm that you want to reopen"
    )

    def __init__(self, *args, **kwargs):
        super(ReopenSvigForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Reopen", css_class="btn btn-danger w-100")
        )


class ClinicalClassForm(forms.Form):
    """
    Add a sample wide comment

    """

    clinical_class = forms.ChoiceField(choices=CLINICAL_CLASS_CHOICES)
    reporting_comment = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        required=False,
        label="Reporting comments:",
    )

    def __init__(self, *args, **kwargs):

        self.check = kwargs.pop("check")

        super(ClinicalClassForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["clinical_class"].initial = self.check.final_clinical_class
        self.fields["reporting_comment"].initial = self.check.reporting_comment
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Update clinical classification", css_class="btn btn-info")
        )


class FinaliseCheckForm(forms.Form):
    """
    Form to close a checkand specify the next action

    """

    NEXT_STEP_CHOICES = (
        ("E", "Send for another check"),
        ("C", "Analysis complete"),
        ("B", "Send back to previous checker"),
    )
    next_step = forms.ChoiceField(choices=NEXT_STEP_CHOICES)
    finalise_check = forms.BooleanField(
        required=True, label="Confirm that analysis is complete"
    )

    def __init__(self, *args, **kwargs):
        super(FinaliseCheckForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Complete check", css_class="btn btn-danger w-100")
        )
