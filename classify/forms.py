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
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "New", css_class="btn btn-info w-100"))


class CompleteCheckInfoForm(forms.Form):
    """
    Form that users tick to confirm they've checked the patient/variant info tab

    """
    complete_check_info_form = forms.BooleanField(
        required=True, label="Confirm that the information on this page is correct"
    )

    def __init__(self, *args, **kwargs):
        super(CompleteCheckInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Confirm", css_class="btn btn-info w-100")
        )


class CompletePreviousClassificationsForm(forms.Form):
    """
    Choose whether to use a previous class of start a new one

    """
    use_previous_class = forms.ChoiceField(label="Choose next step")
    confirm_use_previous_class = forms.BooleanField(
        required=True, label="Confirm decision"
    )

    def __init__(self, *args, **kwargs):
        self.previous_class_choices = kwargs.pop("previous_class_choices")

        super(CompletePreviousClassificationsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.fields["use_previous_class"].choices = self.previous_class_choices
        self.helper.add_input(
            Submit("submit", "Submit", css_class="btn btn-info w-100")
        )


class CompleteClassificationForm(forms.Form):
    """
    Form to complete the classification tab

    """

    # choicefield will be populated depending on the guideline
    override = forms.ChoiceField()
    complete_classification = forms.BooleanField(
        required=True, label="Confirm analysis is complete"
    )

    def __init__(self, *args, **kwargs):
        classification_options = kwargs.pop("classification_options")
        self.CLASS_CHOICES = (("No", "No override"),) + classification_options
        super(CompleteClassificationForm, self).__init__(*args, **kwargs)
        self.fields['override'].choices = self.CLASS_CHOICES
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Complete", css_class="btn btn-info w-100")
        )


class CompleteAnalysisForm(forms.Form):
    """
    Form to close a check and specify the next action

    """
    NEXT_STEP_CHOICES = (
        ("extra_check", "Send for another check"),
        ("complete", "Analysis complete"),
        ("send_back", "Send back to previous checker"),
    )
    next_step = forms.ChoiceField(choices=NEXT_STEP_CHOICES)
    complete_analysis_form = forms.BooleanField(
        required=True, label="Confirm that analysis is complete"
    )

    def __init__(self, *args, **kwargs):
        super(CompleteAnalysisForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Complete check", css_class="btn btn-danger w-100")
        )


class GenericReopenForm(forms.Form):
    """
    Generic form to be inherited by all reopen forms
    """
    def __init__(self, *args, **kwargs):
        super(GenericReopenForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Reopen", css_class="btn btn-danger w-100")
        )


class ReopenCheckInfoForm(GenericReopenForm):
    """
    Form to reset the check info form
    """
    reopen_check_info_form = forms.BooleanField(
        required=True,
        label="Confirm that you want to reopen and that any analysis you've done so far will be wiped",
    )


class ReopenPreviousClassificationsForm(GenericReopenForm):
    """
    Form to reopen the previous classifications form
    """
    reopen_previous_class_form = forms.BooleanField(
        required=True,
        label="Confirm that you want to reopen and that any interpretation you've done so far will be wiped",
    )


class ReopenClassificationForm(GenericReopenForm):
    """
    Form to reopen the previous classifications form
    """
    reopen_classification_check = forms.BooleanField(
        required=True, label="Confirm that you want to reopen"
    )


class ReopenAnalysisForm(GenericReopenForm):
    """
    Form to reopen a case that was previously closed
    """
    reopen_analysis_form = forms.BooleanField(
        required=True, label="Confirm that you want to reopen"
    )
