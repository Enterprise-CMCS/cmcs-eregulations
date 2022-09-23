from rest_framework import serializers


# Allows details of specified fields to be shown or hidden
# Must specify "optional_details" as map of strings to 4-tuples:
#    { "field_name": ("query_param", "default, true or false as a string", serializer class, many=True or False) }
class OptionalFieldDetailsMixin:
    def get_fields(self):
        fields = super().get_fields()
        for i in self.optional_details.items():
            fields[i[0]] = (
                i[1][2](many=i[1][3])
                if self.context.get(i[1][0], i[1][1]).lower() == "true"
                else serializers.PrimaryKeyRelatedField(many=i[1][3], read_only=True)
            )
        return fields


# Retrieves automatically generated search headlines
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
            data = self.get_serializer_map()[instance_type][1](instance=instance, context=self.context).data
            data["type"] = self.get_serializer_map()[instance_type][0]
            return data
        return "Serializer not available"
