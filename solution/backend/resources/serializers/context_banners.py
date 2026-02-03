from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from resources.models import (
    Section,
    Subpart,
)


class ContextBannerSerializer(serializers.Serializer):
    html = serializers.CharField(source='banner_html')
    section = serializers.SerializerMethodField()
    subpart = serializers.SerializerMethodField()

    def get_section(self, obj):
        if type(obj.citation) is Section:
            return f"{obj.citation.part}.{obj.citation.section_id}"
        return None

    def get_subpart(self, obj):
        if type(obj.citation) is Subpart:
            return obj.citation.subpart_id
        if type(obj.citation) is Section and obj.citation.parent:
            return obj.citation.parent.subpart_id
        return None
