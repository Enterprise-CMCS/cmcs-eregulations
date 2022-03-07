from rest_framework import serializers

from regcore.models import Title

class ContentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = "__all__"
