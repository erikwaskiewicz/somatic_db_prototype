from django import forms
from django.template.defaultfilters import linebreaks_filter
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML
from crispy_forms.bootstrap import InlineCheckboxes, InlineRadios

from .models import ClassificationCriteria, Classification

def get_choices_and_help_message(list_of_codes):

    # query for the codes of interest
    codes = ClassificationCriteria.objects.filter(
        code__code__in=list_of_codes
    )

    # For choices we want a list of code/strength combos
    choices = [(choice.id, choice.form_display()) for choice in codes]
    choices.append((None, "None Apply"))

    # for help we want a list of codes and their descriptions formatted for rendering
    help_messages = [(choice.code.code, choice.code.description) for choice in codes]
    help_messages_text = ""
    used_codes = []
    for message in help_messages:
        if message[0] not in used_codes:
            text = message[1].replace('\n', ' ')
            text = text.replace('\r', ' ')
            formatted_message = rf"{message[0]}: {text}<br>"
            help_messages_text += formatted_message
            used_codes.append(message[0])

    return choices, help_messages_text

class ClassifyForm(forms.Form):
    """
    Classify a single variant
    """

    # Population Evidence
    population_choices, population_help = get_choices_and_help_message(["PS4", "PM2", "BA1", "BS1", "BS2"])
    population_codes = forms.MultipleChoiceField(
        label = "Population Evidence",
        help_text = mark_safe(population_help),
        choices = population_choices,
        widget=forms.CheckboxSelectMultiple
    )

    # Predictive and Computational Evidence
    predictive_choices, predictive_help = get_choices_and_help_message(["PVS1", "PS1", "PM5", "PM4", "PP3", "BP1", "BP4", "BP7"])
    predictive_codes = forms.MultipleChoiceField(
        label = "Predictive and Computational Evidence",
        help_text = mark_safe(predictive_help),
        choices = predictive_choices,
        widget = forms.CheckboxSelectMultiple
    )

    # Functional Evidence
    functional_choices, functional_help = get_choices_and_help_message(["PS3", "PM1", "PP2", "BS3"])
    functional_codes = forms.MultipleChoiceField(
        label = "Functional Evidence",
        help_text = mark_safe(functional_help),
        choices = functional_choices,
        required=False,
        widget = forms.CheckboxSelectMultiple
    )

    # De Novo Evidence
    de_novo_choices, de_novo_help = get_choices_and_help_message(["PS2", "PM6"])
    de_novo_codes = forms.ChoiceField(
        label = "De Novo Evidence",
        help_text = mark_safe(de_novo_help),
        choices = de_novo_choices
    )

    # Segregation Evidence
    segregation_choices, segregation_help = get_choices_and_help_message(["PP1", "BS4"])
    segregation_codes = forms.ChoiceField(
        label = "Segregation Evidence",
        help_text = mark_safe(segregation_help),
        choices = segregation_choices
    )

    # Allelic Evidence
    allelic_choices, allelic_help = get_choices_and_help_message(["PM3", "BP2"])
    allelic_codes = forms.ChoiceField(
        label = "Allelic Evidence",
        help_text = mark_safe(allelic_help),
        choices = allelic_choices
    )

    # Phenotype Data
    phenotype_choices, phenotype_help = get_choices_and_help_message(["PP4", "BP5"])
    phenotype_codes = forms.ChoiceField(
        label = "Phenotype Evidence",
        help_text = mark_safe(phenotype_help),
        choices = phenotype_choices
    )

    def __init__(self, *args, **kwargs):
        super(ClassifyForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.label_class = "font-weight-bold"
        self.helper.add_input(
            Submit("submit", "Classify Variant", css_class="btn btn-info w-100")
            )
        
        self.helper.layout = Layout(   
            InlineCheckboxes("population_codes"),
            InlineCheckboxes("predictive_codes"),
            InlineCheckboxes("functional_codes"),
            InlineRadios("de_novo_codes"),
            InlineRadios("segregation_codes"),
            InlineRadios("allelic_codes"),
            InlineRadios("phenotype_codes")
        )
