from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, OpenApiTypes


# Retrieves automatically generated search headlines
@extend_schema_field(OpenApiTypes.STR)
class HeadlineField(serializers.Field):
    def __init__(self, model_name, **kwargs):
        self.model_name = model_name
        kwargs["source"] = '*'
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, obj):
        return getattr(obj, f"{self.model_name}_{self.field_name}", getattr(obj, self.field_name, None))


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
