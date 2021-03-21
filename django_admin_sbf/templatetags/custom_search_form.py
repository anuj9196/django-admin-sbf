from django.contrib.admin.views.main import SEARCH_VAR
from django import template

register = template.Library()


@register.inclusion_tag('admin/custom_search_form.html', takes_context=False)
def advanced_search_form(cl):
    """
    Displays a search form for searching the list.
    """
    return {
        'cl': cl,
        'show_result_count': cl.result_count != cl.full_result_count,
        'search_var': SEARCH_VAR
    }
