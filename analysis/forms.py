from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
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