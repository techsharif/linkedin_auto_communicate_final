from django import template

register = template.Library()

@register.simple_tag
def site_title():
    return "B2B Prospecting"