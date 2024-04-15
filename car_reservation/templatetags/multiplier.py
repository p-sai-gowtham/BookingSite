from django import template

register = template.Library()

# "{:.2f}".format(value * arg)


@register.filter
def multiply(value, arg):
    return "{:.2f}".format(value * arg)
