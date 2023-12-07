from drf_spectacular.utils import PolymorphicProxySerializer


class ProxySerializerWrapper:
    def __init__(self, component_name, serializers, resource_type_field_name):
        self.many_true, self.many_false = [PolymorphicProxySerializer(
            component_name=component_name,
            serializers=serializers,
            resource_type_field_name=resource_type_field_name,
            many=i,
        ) for i in [True, False]]

    def many(self, many):
        return self.many_true if many else self.many_false
