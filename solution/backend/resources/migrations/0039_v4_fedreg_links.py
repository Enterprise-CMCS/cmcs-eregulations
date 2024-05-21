from django.db import migrations


def copy_federal_register_links(apps, schema_editor):
    FederalRegisterDocument = apps.get_model("resources", "FederalRegisterDocument")
    FederalRegisterLink = apps.get_model("resources", "FederalRegisterLink")
    NewSubject = apps.get_model("resources", "NewSubject")
    AbstractCitation = apps.get_model("resources", "AbstractCitation")
    AbstractPublicCategory = apps.get_model("resources", "AbstractPublicCategory")

    categories = AbstractPublicCategory.objects.in_bulk(field_name="old_pk")

    for i in FederalRegisterDocument.objects.all():
        link = FederalRegisterLink.objects.create(
            old_pk=i.pk,
            created_at=i.created_at,
            updated_at=i.updated_at,
            approved=i.approved,
            category=categories[i.category.pk] if i.category else None,
            cfr_citation_history=i.location_history,
            act_citations=i.statute_locations,
            usc_citations=i.usc_locations,
            editor_notes=i.internal_notes or "",
            document_id=i.name or "",
            title=i.description or "",
            date=i.date or "",
            url=i.url or "",
            extract_url=i.url or "",
            document_id_sort=i.name_sort,
            title_sort=i.description_sort,
            docket_numbers=i.docket_numbers,
            document_number=i.document_number or "",
            correction=i.correction,
            withdrawal=i.withdrawal,
            action_type=i.doc_type or "",
        )

        link.cfr_citations.set(AbstractCitation.objects.filter(old_pk__in=i.locations.all().values_list("pk", flat=True)))
        link.subjects.set(NewSubject.objects.filter(old_pk__in=i.subjects.all().values_list("pk", flat=True)))
        link.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0038_v4_public_links'),
    ]

    operations = [
        migrations.RunPython(copy_federal_register_links),
    ]
