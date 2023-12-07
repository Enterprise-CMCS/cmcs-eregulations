from drf_spectacular.utils import OpenApiTypes, extend_schema_field
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from .api import OpenApiQueryParameter

# For viewsets where pagination is disabled by default
PAGINATION_PARAMS = [
    OpenApiQueryParameter("page", "A page number within the paginated result set.", int, False),
    OpenApiQueryParameter("page_size", "Number of results to return per page.", int, False),
]


class ViewSetPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 1000
    page_size = 100


# May define "paginate_by_default = False" to disable pagination unless explicitly requested
# Pagination can be enabled/disabled with "?paginate=true/false"
class OptionalPaginationMixin:
    PARAMETERS = [
        OpenApiQueryParameter("paginate", "Enable or disable pagination. If enabled, results will be wrapped in a JSON object. "
                              "If disabled, a normal JSON array will be returned.", bool, False),
    ]

    paginate_by_default = True

    @property
    def pagination_class(self):
        paginate = self.request.GET.get(
            "paginate",
            "true" if self.paginate_by_default else "false"
        ).lower() == "true"
        return ViewSetPagination if paginate else None


class DisplayNameFieldMixin:
    @property
    def display_name(self):
        return str(self)


# Allows subclasses to be serialized independently
# Must implement get_serializer_map as map of classes to 2-tuples:
#    { model_class: ("model_name", serializer_class) }
class PolymorphicSerializer(serializers.Serializer):
    def get_serializer_map(self):
        raise NotImplementedError

    def to_representation(self, instance):
        instance_type = type(instance)
        if instance_type in self.get_serializer_map():
            setattr(instance, "type", self.get_serializer_map()[instance_type][0])
            return self.get_serializer_map()[instance_type][1](instance=instance, context=self.context).data
        return "Serializer not available"


# Permits a "type" field to be properly displayed by polymorphic serializers (e.g. { "type": "Section" })
@extend_schema_field(OpenApiTypes.STR)
class PolymorphicTypeField(serializers.Field):
    def __init__(self, **kwargs):
        kwargs["source"] = '*'
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, obj):
        return getattr(obj, self.field_name, "")
