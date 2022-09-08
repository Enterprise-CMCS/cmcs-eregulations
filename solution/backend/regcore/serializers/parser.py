from rest_framework import serializers
from django.apps import apps

from regcore.models import ECFRParserResult


class ParserResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ECFRParserResult
        fields = '__all__'


class SectionCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    part = serializers.CharField()
    section = serializers.CharField()


class SubpartCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    part = serializers.CharField()
    subpart = serializers.CharField()
    sections = SectionCreateSerializer(many=True)


class PartUploadSerializer(serializers.Serializer):
    # part fields
    name = serializers.CharField()
    title = serializers.CharField()
    date = serializers.DateField()
    document = serializers.JSONField()
    structure = serializers.JSONField()
    depth = serializers.IntegerField()

    # location fields
    sections = SectionCreateSerializer(many=True)
    subparts = SubpartCreateSerializer(many=True)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name")
        instance.title = validated_data.get("title")
        instance.date = validated_data.get("date")
        instance.document = validated_data.get("document")
        instance.structure = validated_data.get("structure")
        instance.depth = validated_data.get("depth")

        if apps.is_installed("resources"):
            from resources.models import Section, Subpart  # can throw ImportError, this is fine

            for section in validated_data.get("sections", []):
                new_orphan_section, created = Section.objects.get_or_create(
                    title=section["title"],
                    part=section["part"],
                    section_id=section["section"],
                )
            
            for subpart in validated_data.get("subparts", []):
                new_subpart, created = Subpart.objects.get_or_create(
                    title=subpart["title"],
                    part=subpart["part"],
                    subpart_id=subpart["subpart"],
                )

                for section in subpart["sections"]:
                    new_section, created = Section.objects.update_or_create(
                        title=section["title"],
                        part=section["part"],
                        section_id=section["section"],
                        defaults={"parent": new_subpart},
                    )

        instance.save()
        return instance
