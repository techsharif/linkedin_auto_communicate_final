from django import template
from jetbuzz.settings import SITE_TITLE
register = template.Library()


@register.simple_tag
def site_title():
    return SITE_TITLE
