from rest_framework import serializers


class DivisionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()


class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()


class GroupWithDivisionSerializer(GroupSerializer):
    divisions = DivisionSerializer(many=True)


class DivisionWithGroupSerializer(DivisionSerializer):
    group = GroupSerializer()
