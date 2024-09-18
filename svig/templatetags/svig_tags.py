from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def colour_by_class(value):
    """
    colour anywhere the current classification is displayed
    e.g. smmary buttons, dropdowns, table rows
    """
    value = value.lower()
    if value == "pending" or value == "vus":
        css_class = "warning"

    elif value.startswith("b") or "benign" in value:
        css_class = "primary"

    elif value.startswith("o") or "oncogenic" in value:
        css_class = "danger"

    elif value.startswith("tier"):
        if value == "tier iii":
            css_class = "warning"
        elif value == "tier iv":
            css_class = "primary"
        else:
            css_class = "danger"

    else:
        css_class = "secondary"

    return css_class


@register.filter
@stringfilter
def colour_by_build(value):
    """
    Colour anywhere the genome build is displayed
    """
    if value == "38":
        return "success"
    else:
        return "info"
