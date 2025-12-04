from django.contrib.admin import SimpleListFilter
from django.db.models import Q


class InputFilter(SimpleListFilter):
    template = 'input_filter.html'

    def lookups(self, request, model_admin):
        return ((),)

    def choices(self, changelist):
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class ParameterFilter(InputFilter):
    parameter_name = None
    title = None

    def queryset(self, request, queryset):
        if self.value() is not None and self.parameter_name is not None and self.title is not None:
            value = self.value()
            filter = {self.parameter_name: value}
            return queryset.filter(**filter).distinct()


class IndexPopulatedFilter(SimpleListFilter):
    title = "index populated"
    parameter_name = "populated"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(Q(indices__content__isnull=False) & ~Q(indices__content__exact=""))
        if self.value() == "no":
            return queryset.filter(Q(indices__content__isnull=True) | Q(indices__content__exact=""))
        return queryset
