from rest_framework import serializers


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class MiniNodeSerializer(serializers.Serializer):
    node_type = serializers.CharField()
    header = serializers.CharField()
    content = serializers.CharField()


class PartNodeSerializer(serializers.Serializer):
    label = serializers.ListField(child=serializers.CharField())
    node_type = serializers.CharField()
    title = serializers.CharField()
    node_type = serializers.CharField()
    header = serializers.CharField()
    content = serializers.CharField()
    src = serializers.CharField()

    authority = MiniNodeSerializer()
    source = MiniNodeSerializer()
    editorial_node = MiniNodeSerializer()

    children = RecursiveField(many=True)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     data = args[0]
    #     remove_fields = []
    #     for field in self.fields:
    #         if field not in data:
    #             remove_fields.append(field)
    #     [self.fields.pop(field) for field in remove_fields]
