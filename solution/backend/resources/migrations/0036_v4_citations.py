from django.db import migrations


def copy_citations(apps, schema_editor):
    NewSubpart = apps.get_model("resources", "NewSubpart")
    NewSection = apps.get_model("resources", "NewSection")
    OldSubpart = apps.get_model("resources", "Subpart")
    OldSection = apps.get_model("resources", "Section")

    sections = list(OldSection.objects.all().values_list("pk", flat=True))

    for i in OldSubpart.objects.all():
        parent = NewSubpart.objects.create(
            title=i.title,
            part=i.part,
            subpart_id=i.subpart_id,
            old_pk=i.pk,
        )
        for j in i.children.all():
            NewSection.objects.create(
                title=j.title,
                part=j.part,
                section_id=j.section_id,
                old_pk=j.pk,
                parent=parent,
            )
            sections.remove(j.pk)

    for i in OldSection.objects.filter(pk__in=sections):
        NewSection.objects.create(
            title=i.title,
            part=i.part,
            section_id=i.section_id,
            old_pk=i.pk,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0035_v4_categories'),
    ]

    operations = [
        migrations.RunPython(copy_citations),
    ]
