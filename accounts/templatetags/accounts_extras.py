from re import I

from country_list import countries_for_language
from django import template

register = template.Library()

@register.filter
def find_country(inital_name: str) -> str:
    """
    Returns coutnry's full name. example('IL' -> 'Israel')
    """
    COUNTRIES = dict(countries_for_language('en'))
    return COUNTRIES[inital_name]