from rest_framework import serializers


class PolymorphicSerializer(serializers.Serializer):
    def get_serializer_map(self):
        raise NotImplementedError()

    def to_representation(self, obj):
        data = super().to_representation(obj)
        for subclass in self.Meta.model.__subclasses__():
            name = subclass.__name__.lower()
            child = getattr(obj, name, None)
            if child:
                data["type"] = name
                serializer = self.get_serializer_map().get(subclass, None)
                if serializer:
                    return {**data, **(serializer(child, context=self.context).to_representation(child))}
        return data
