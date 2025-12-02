from rest_framework import serializers

from common.fields import HeadlineField
from resources.serializers import AbstractResourceSerializer


class IndexedRegulationTextSerializer(serializers.Serializer):
    title = serializers.IntegerField()
    date = serializers.CharField()
    part_title = serializers.CharField()
    part_number = serializers.IntegerField()
    subpart_title = serializers.CharField()
    subpart_id = serializers.CharField()
    node_type = serializers.CharField()
    node_id = serializers.CharField()
    node_title = serializers.CharField()


class ContentSearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(max_length=10000, help_text="The search query string.")
    page = serializers.IntegerField(required=False, default=1, help_text="The page number for paginated results.")
    page_size = serializers.IntegerField(required=False, default=30, help_text="The number of results per page.")
    show_public = serializers.BooleanField(
        required=False,
        default=True,
        help_text="Whether to include public resources in the search results.",
    )
    show_internal = serializers.BooleanField(
        required=False,
        default=True,
        help_text="Whether to include internal resources in the search results.",
    )
    show_regulations = serializers.BooleanField(
        required=False,
        default=True,
        help_text="Whether to include regulation text in the search results.",
    )
    categories = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of category IDs to filter results by.",
    )
    citations = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of citation strings to filter results by.",
    )
    subjects = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of subject IDs to filter results by.",
    )


class ContentSearchSerializer(serializers.Serializer):
    name_headline = HeadlineField()
    summary_headline = HeadlineField()
    content_headline = HeadlineField()

    resource = AbstractResourceSerializer()
    reg_text = IndexedRegulationTextSerializer()

    def to_representation(self, instance):
        blank_headline_fields = self.context.get("blank_headline_fields", [])
        for field in blank_headline_fields:
            if field in self.fields:
                self.fields[field].blank_when_no_highlight = True
        representation = super().to_representation(instance)
        return representation


class SubjectCountSerializer(serializers.Serializer):
    subject = serializers.IntegerField()
    count = serializers.IntegerField()


class CategoryCountSerializer(serializers.Serializer):
    category = serializers.IntegerField()
    parent = serializers.IntegerField()
    count = serializers.IntegerField()


class ContentCountSerializer(serializers.Serializer):
    internal_resource_count = serializers.IntegerField()
    public_resource_count = serializers.IntegerField()
    regulation_text_count = serializers.IntegerField()

    subjects = SubjectCountSerializer(many=True)
    categories = CategoryCountSerializer(many=True)


class ChunkUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    chunk_index = serializers.IntegerField(required=True)
    total_chunks = serializers.IntegerField(required=True)
    file_type = serializers.CharField(required=False, default="")
    error = serializers.CharField(required=False, default="")
    text = serializers.CharField(required=False, default="")
    embedding = serializers.ListField(child=serializers.FloatField(), required=False, default=list)
