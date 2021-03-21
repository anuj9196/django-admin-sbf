from django.contrib.admin.views.main import ChangeList, ChangeListSearchForm
from django import forms


ADVANCED_SEARCH_FIELD = 'f'


class AdminSearchForm(ChangeListSearchForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add advanced search field to the form
        self.fields.update({
            ADVANCED_SEARCH_FIELD: forms.CharField(required=False, strip=False)
        })


class CustomChangeList(ChangeList):
    search_form_class = AdminSearchForm

    def __init__(self, request, model, list_display, list_display_links,
                 list_filter, date_hierarchy, search_fields, list_select_related,
                 list_per_page, list_max_show_all, list_editable, model_admin, sortable_by):
        super().__init__(request, model, list_display, list_display_links,
                         list_filter, date_hierarchy, search_fields, list_select_related,
                         list_per_page, list_max_show_all, list_editable, model_admin, sortable_by)

        # Add the field data to be used in the template
        # To mark the list item as selected
        self.field_ = request.GET.get(ADVANCED_SEARCH_FIELD)

    def get_filters(self, request):
        """
        Override the get_filters method.
        Get all filter attributes from the parent get_filters method
        Remove the `f` (search field key) from the remaining lookup params
        Return filter attributes with the updated data

        :param request:
        :return:
        """

        # Get filters attributes from parent
        (
            filter_specs,
            has_filters,
            remaining_lookup_params,
            filters_use_distinct,
            has_active_filters,
        ) = super().get_filters(request)

        # If remaining lookup params has the advanced search field, remove the same from the dict
        # Otherwise it will IncorrectLookupParameters exception from
        # django.contrib.admin.views.main.py (Line 484)
        if remaining_lookup_params.get(ADVANCED_SEARCH_FIELD, None):
            del remaining_lookup_params[ADVANCED_SEARCH_FIELD]

        return (
            filter_specs,
            has_filters,
            remaining_lookup_params,
            filters_use_distinct,
            has_active_filters
        )
