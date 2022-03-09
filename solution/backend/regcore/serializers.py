from rest_framework import serializers

from regcore.models import Title

class ContentsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.toc


class VersionsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.date
