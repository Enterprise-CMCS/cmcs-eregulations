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


def create_category_params(from_obj):
    return {
        "name": from_obj.name or "",
        "description": from_obj.description or "",
        "order": from_obj.order,
        "show_if_empty": from_obj.show_if_empty,
        "old_pk": from_obj.pk,
    }


def copy_categories(OldCategory, OldSubCategory, NewCategory, NewSubCategory):
    # Create a list of subcategories
    subcategories = list(OldSubCategory.objects.all().values_list("pk", flat=True))

    for i in OldCategory.objects.all():
        # Create the parent category
        parent = NewCategory.objects.create(**create_category_params(i))
        # Create all subcategories of the parent, if they exist
        for j in i.sub_categories.all():
            NewSubCategory.objects.create(**{
                **create_category_params(j),
                **{"parent": parent}
            })
            subcategories.remove(j.pk)  # Remove the subcategory from this list so we don't create it twice
    
    # Create subcategories that do not have parents, if they exist
    for i in OldSubCategory.objects.filter(pk__in=subcategories):
        NewSubCategory.objects.create(**create_category_params(i))


def copy_public_categories(apps, schema_editor):
    OldCategory = apps.get_model("resources", "Category")
    OldSubCategory = apps.get_model("resources", "SubCategory")
    PublicCategory = apps.get_model("resources", "PublicCategory")
    PublicSubCategory = apps.get_model("resources", "PublicSubCategory")

    copy_categories(OldCategory, OldSubCategory, PublicCategory, PublicSubCategory)


def copy_internal_categories(apps, schema_editor):
    if not apps.is_installed("file_manager"):
        return  # Skip copying repo categories
    try:
        RepoCategory = apps.get_model("file_manager", "RepositoryCategory")
        RepoSubCategory = apps.get_model("file_manager", "RepositorySubCategory")
    except Exception:
        return  # Failed to import needed models, skip copying repo categories

    InternalCategory = apps.get_model("resources", "InternalCategory")
    InternalSubCategory = apps.get_model("resources", "InternalSubCategory")

    copy_categories(RepoCategory, RepoSubCategory, InternalCategory, InternalSubCategory)


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


def copy_subjects(apps, schema_editor):
    if not apps.is_installed("file_manager"):
        return  # Skip copying repo subjects
    try:
        OldSubject = apps.get_model("file_manager", "Subject")
    except Exception:
        return  # Failed to import needed models, skip copying repo subjects
    NewSubject = apps.get_model("resources", "NewSubject")

    for i in OldSubject.objects.all():
        NewSubject.objects.create(
            full_name=i.full_name or "",
            short_name=i.short_name or "",
            abbreviation=i.abbreviation or "",
            combined_sort=i.combined_sort,
            old_pk=i.pk,
        )


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


def copy_internal_files(apps, schema_editor):
    if not apps.is_installed("file_manager"):
        return  # Skip copying repo files
    try:
        UploadedFile = apps.get_model("file_manager", "UploadedFile")
    except Exception:
        return  # Failed to import needed models, skip copying repo files

    InternalFile = apps.get_model("resources", "InternalFile")
    NewSubject = apps.get_model("resources", "NewSubject")
    AbstractCitation = apps.get_model("resources", "AbstractCitation")
    AbstractInternalCategory = apps.get_model("resources", "AbstractInternalCategory")

    categories = AbstractInternalCategory.objects.in_bulk(field_name="old_pk")

    for i in UploadedFile.objects.all():
        file = InternalFile.objects.create(
            old_pk=i.pk,
            approved=True,
            category=categories[i.category.pk] if i.category else None,
            editor_notes=i.internal_notes or "",
            document_id=i.document_name or "",
            summary=i.summary or "",
            created_at=i.updated_at,
            updated_at=i.updated_at,
            date=i.date or "",
            file_name=i.file_name or "",
            uid=i.uid,
        )

        file.cfr_citations.set(AbstractCitation.objects.filter(old_pk__in=i.locations.all().values_list("pk", flat=True)))
        file.subjects.set(NewSubject.objects.filter(old_pk__in=i.subjects.all().values_list("pk", flat=True)))
        file.save()


def copy_resource_groups(apps, schema_editor):
    FederalRegisterDocumentGroup = apps.get_model("resources", "FederalRegisterDocumentGroup")
    ResourceGroup = apps.get_model("resources", "ResourceGroup")
    FederalRegisterLink = apps.get_model("resources", "FederalRegisterLink")

    for i in FederalRegisterDocumentGroup.objects.all():
        # If docket_number_prefixes is a name instead of a prefix, then fill the 'name' field instead.
        if len(i.docket_number_prefixes) == 1 and not i.docket_number_prefixes[0].endswith("-"):
            kwargs = {"name": i.docket_number_prefixes[0]}
        else:
            kwargs = {"common_identifiers": i.docket_number_prefixes}

        group = ResourceGroup.objects.create(**kwargs)

        old_resources = i.documents.all().values_list("pk", flat=True)
        group.resources.set(FederalRegisterLink.objects.filter(old_pk__in=old_resources))
        group.save()

        query = group.resources.all().order_by("-date")
        if not query:
            continue
        first = query[0]

        query = group.resources.aggregate(
            all_citations=ArrayAgg("cfr_citations", distinct=True, filter=Q(cfr_citations__isnull=False)),
            all_subjects=ArrayAgg("subjects", distinct=True, filter=Q(subjects__isnull=False)),
        )

        group.cfr_citations.set(query["all_citations"] or [])
        group.subjects.set(query["all_subjects"] or [])
        group.category = first.category
        group.date = first.date
        group.save()


def copy_resources_config(apps, schema_editor):
    OldResourcesConfiguration = apps.get_model("resources", "ResourcesConfiguration")
    NewResourcesConfiguration = apps.get_model("resources", "NewResourcesConfiguration")
    AbstractPublicCategory = apps.get_model("resources", "AbstractPublicCategory")
    old = OldResourcesConfiguration.objects.first()
    new, _ = NewResourcesConfiguration.objects.get_or_create()
    if old and old.fr_doc_category:
        try:
            new.fr_link_category = AbstractPublicCategory.objects.get(old_pk=old.fr_doc_category.pk)
            new.save()
        except AbstractPublicCategory.DoesNotExist:
            pass


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('resources', '0034_v4_refactor_models'),
    ]

    operations = [
        migrations.RunPython(partial(migration, copy_public_categories), atomic=True),
        migrations.RunPython(partial(migration, copy_internal_categories), atomic=True),
        migrations.RunPython(partial(migration, copy_citations), atomic=True),
        migrations.RunPython(partial(migration, copy_subjects), atomic=True),
        migrations.RunPython(partial(migration, copy_public_links), atomic=True),
        migrations.RunPython(partial(migration, copy_federal_register_links), atomic=True),
        migrations.RunPython(partial(migration, copy_internal_files), atomic=True),
        migrations.RunPython(partial(migration, copy_resource_groups), atomic=True),
        migrations.RunPython(partial(migration, copy_resources_config), atomic=True),
    ]
