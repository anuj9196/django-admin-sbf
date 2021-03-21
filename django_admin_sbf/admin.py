import operator
from functools import reduce

from django.contrib.admin import ModelAdmin
from django.contrib.admin.utils import lookup_needs_distinct
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models.constants import LOOKUP_SEP


class DjangoAdminSBF(ModelAdmin):
    """
    Extend this class to add advanced search in the admin panel
    """

    change_list_template = 'admin/custom_change_list.html'

    def get_changelist(self, request, **kwargs):
        from .admin_forms import CustomChangeList
        return CustomChangeList

    def get_search_results(self, request, queryset, search_term):

        # Apply keyword searches.
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            # Use field_name if it includes a lookup.
            opts = queryset.model._meta
            lookup_fields = field_name.split(LOOKUP_SEP)
            # Go through the fields, following all relations.
            prev_field = None
            for path_part in lookup_fields:
                if path_part == 'pk':
                    path_part = opts.pk.name
                try:
                    field = opts.get_field(path_part)
                except FieldDoesNotExist:
                    # Use valid query lookups.
                    if prev_field and prev_field.get_lookup(path_part):
                        return field_name
                else:
                    prev_field = field
                    if hasattr(field, 'get_path_info'):
                        # Update opts to follow the relation.
                        opts = field.get_path_info()[-1].to_opts
            # Otherwise, use the field with icontains.
            return "%s__icontains" % field_name

        query_field_params = request.GET.get('f', None)
        print('query_params_________: {}'.format(query_field_params))

        use_distinct = False
        search_fields = self.get_search_fields(request)
        print('search_fields________: {}'.format(search_fields))
        print('search term__________: {}'.format(search_term))
        if search_fields and search_term and query_field_params in search_fields:
            # orm_lookups = [construct_search(str(search_field))
            #                for search_field in search_fields]
            orm_lookups = [construct_search(str(query_field_params))]
            for bit in search_term.split():
                or_queries = [models.Q(**{orm_lookup: bit})
                              for orm_lookup in orm_lookups]
                queryset = queryset.filter(reduce(operator.or_, or_queries))
            use_distinct |= any(lookup_needs_distinct(self.opts, search_spec) for search_spec in orm_lookups)

        # traceback.print_stack()
        # return super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct
