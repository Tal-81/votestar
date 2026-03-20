"""topics/templatetags/topic_tags.py"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Allow dict[key] access in templates: {{ my_dict|get_item:key }}"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def star_range(value):
    """Return range(1, value+1) for iteration."""
    try:
        return range(1, int(value) + 1)
    except (TypeError, ValueError):
        return range(0)
