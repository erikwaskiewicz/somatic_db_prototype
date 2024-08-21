from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class DownloadCsvForm(forms.Form):
    """
    Download a csv of variants from SVD
    TEMPORARY FUNCTIONALITY FOR VALIDATION ONLY
    """

    def __init__(self, *args, **kwargs):
        super(DownloadCsvForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(
            Submit("submit", "Download CSV", css_class="btn btn-info w-100")
            )
