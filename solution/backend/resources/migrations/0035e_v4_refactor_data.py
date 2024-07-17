from functools import partial

import common.fields
import common.mixins
import django.core.validators
import django.db.models.deletion
import django_jsonform.models.fields
from django.db import migrations, models
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q


TIMEOUT_MINUTES = 10


def migration(func, apps, schema_editor):
    schema_editor.execute(f"SET LOCAL statement_timeout TO {TIMEOUT_MINUTES * 60000};")
    func(apps, schema_editor)


def copy_public_links(apps, schema_editor):
    SupplementalContent = apps.get_model("resources", "SupplementalContent")
    PublicLink = apps.get_model("resources", "PublicLink")
    NewSubject = apps.get_model("resources", "NewSubject")
    AbstractCitation = apps.get_model("resources", "AbstractCitation")
    AbstractPublicCategory = apps.get_model("resources", "AbstractPublicCategory")

    categories = AbstractPublicCategory.objects.in_bulk(field_name="old_pk")

    for i in SupplementalContent.objects.all():
        link = PublicLink.objects.create(
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
        )

        link.cfr_citations.set(AbstractCitation.objects.filter(old_pk__in=i.locations.all().values_list("pk", flat=True)))
        link.subjects.set(NewSubject.objects.filter(old_pk__in=i.subjects.all().values_list("pk", flat=True)))
        link.save()


class Migration(migrations.Migration):
    dependencies = [
        ('resources', '0035d_v4_refactor_data'),
    ]

    operations = [
        migrations.RunPython(partial(migration, copy_public_links)),
    ]
