from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def user_repr(user: User) -> str:
    """
    Returns User instance's username or 'Guest'
    """
    if user.is_authenticated:
        return user
    else:
        return 'Guest'
