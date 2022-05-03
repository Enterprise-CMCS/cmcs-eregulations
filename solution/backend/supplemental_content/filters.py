from django.contrib.admin import SimpleListFilter


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


class TitleFilter(ParameterFilter):
    parameter_name = "locations__title"
    title = "Title"


class PartFilter(ParameterFilter):
    parameter_name = "locations__part"
    title = "Part"


class SectionFilter(ParameterFilter):
    parameter_name = "locations__section__section_id"
    title = "Section"


class SubpartFilter(ParameterFilter):
    parameter_name = "locations__subpart__subpart_id"
    title = "Subpart"
