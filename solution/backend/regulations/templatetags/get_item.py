from django import template

register = template.Library()


@register.simple_tag
def get_item(dictionary, key, default_value):
    return dictionary.get(key, default_value if default_value else '')
