from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def colour_by_class(value):
    value = value.lower()
    if value == "pending":
        css_class = 'warning'

    elif value.startswith("b"):
        css_class = 'info'

    elif value.startswith("o"):
        css_class = 'danger'

    else:
        css_class = 'secondary'

    return css_class
