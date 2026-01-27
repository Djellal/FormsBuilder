from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return ''
    return dictionary.get(key, '')


@register.filter
def is_field_readonly(field, is_admin_user):
    """Returns True if field is admin_only and user is not admin"""
    return field.admin_only and not is_admin_user
