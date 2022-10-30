from django import template

register = template.Library()


@register.filter
def get_value_from_dict(dict_data, key):
    if key:
        return dict_data.get(key)


@register.simple_tag
def organization_acceptable_for_user(user, org_id):
    return not user.is_anonymous and user.organization_admin(org_id)
