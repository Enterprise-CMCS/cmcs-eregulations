from rest_framework import serializers
from django.apps import apps

from regcore.models import ECFRParserResult


class PartConfigurationSerializer(serializers.Serializer):
    title = serializers.IntegerField()
    type = serializers.CharField()
    value = serializers.CharField()
    upload_reg_text = serializers.BooleanField()
    upload_locations = serializers.BooleanField()
    upload_fr_docs = serializers.BooleanField()


class ParserConfigurationSerializer(serializers.Serializer):
    workers = serializers.IntegerField()
    retries = serializers.IntegerField()
    loglevel = serializers.CharField()
    upload_supplemental_locations = serializers.BooleanField()
    log_parse_errors = serializers.BooleanField()
    skip_reg_versions = serializers.BooleanField()
    skip_fr_documents = serializers.BooleanField()
    parts = PartConfigurationSerializer(many=True)


class ParserResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ECFRParserResult
        fields = '__all__'


class PartSectionCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    part = serializers.CharField()
    section = serializers.CharField()


class PartSubpartCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    part = serializers.CharField()
    subpart = serializers.CharField()
    sections = PartSectionCreateSerializer(many=True)


class PartUploadSerializer(serializers.Serializer):
    # part fields
    name = serializers.CharField()
    title = serializers.CharField()
    date = serializers.DateField()
    document = serializers.JSONField()
    structure = serializers.JSONField()
    depth = serializers.IntegerField()

    # location fields
    sections = PartSectionCreateSerializer(many=True)
    subparts = PartSubpartCreateSerializer(many=True)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name")
        instance.title = validated_data.get("title")
        instance.date = validated_data.get("date")
        instance.document = validated_data.get("document")
        instance.structure = validated_data.get("structure")
        instance.depth = validated_data.get("depth")

        # create depth stack for front page TOC
        stack = []
        current = instance.structure
        for i in range(instance.depth + 1):
            structure_copy = current.copy()
            del structure_copy["children"]
            stack.append(structure_copy)
            current = current["children"][0]
        instance.depth_stack = stack

        # load sections and subparts
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
