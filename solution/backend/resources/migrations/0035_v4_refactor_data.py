import common.fields
import common.mixins
import django.core.validators
import django.db.models.deletion
import django_jsonform.models.fields
from django.db import migrations, models


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
    subcategories = OldSubCategory.objects.all().values_list("pk", flat=True)

    for i in OldCategory.objects.all():
        # Create the parent category
        parent = NewCategory.objects.create(**create_category_params(i))
        # Create all subcategories of the parent, if they exist
        for j in i.sub_categories.objects.all():
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
    OldSubpart = apps.get_model("resourcse", "Subpart")
    OldSection = apps.get_model("resources", "Section")

    sections = OldSection.objects.all().values_list("pk", flat=True)

    for i in OldSubpart.objects.all():
        parent = NewSubpart.objects.create(
            title=i.title,
            part=i.part,
            subpart_id=i.subpart_id,
            old_pk=i.pk,
        )
        for j in i.children.objects.all():
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
    NewAbstractCategory = apps.get_model("resources", "NewAbstractCategory")

    subjects = {subject.old_pk: subject for subject in NewSubject.objects.all()}
    citations = {citation.old_pk: citation for citation in AbstractCitation.objects.all()}
    categories = {category.old_pk: category for category in NewAbstractCategory.objects.all()}

    for i in SupplementalContent.objects.all():
        link = PublicLink.objects.create(
            old_pk=i.pk,
            created_at=i.created_at,
            updated_at=i.updated_at,
            approved=i.approved,
            category=categories[i.category.pk],
            citation_history=i.location_history,
            statute_citations=i.statute_citations,
            usc_citations=i.usc_citations,
            internal_notes=i.internal_notes or "",
            name=i.name or "",
            description=i.description or "",
            date=i.date or "",
            url=i.url or "",
            extract_url=i.url or "",
            name_sort=i.name_sort,
            description_sort=i.description_sort,
        )
        link.citations.set([citations[pk] for pk in link.locations.objects.all().values_list("pk", flat=True)])
        link.subjects.set([subjects[pk] for pk in link.subjects.objects.all().values_list("pk", flat=True)])
        link.save()


def copy_federal_register_links(apps, schema_editor):
    FederalRegisterDocument = apps.get_model("resources", "FederalRegisterDocument")
    FederalRegisterLink = apps.get_model("resources", "FederalRegisterLink")
    NewSubject = apps.get_model("resources", "NewSubject")
    AbstractCitation = apps.get_model("resources", "AbstractCitation")
    NewAbstractCategory = apps.get_model("resources", "NewAbstractCategory")

    subjects = {subject.old_pk: subject for subject in NewSubject.objects.all()}
    citations = {citation.old_pk: citation for citation in AbstractCitation.objects.all()}
    categories = {category.old_pk: category for category in NewAbstractCategory.objects.all()}

    for i in FederalRegisterDocument.objects.all():
        link = FederalRegisterLink.objects.create(
            old_pk=i.pk,
            created_at=i.created_at,
            updated_at=i.updated_at,
            approved=i.approved,
            category=categories[i.category.pk],
            citation_history=i.location_history,
            statute_citations=i.statute_citations,
            usc_citations=i.usc_citations,
            internal_notes=i.internal_notes or "",
            name=i.name or "",
            description=i.description or "",
            date=i.date or "",
            url=i.url or "",
            extract_url=i.url or "",
            name_sort=i.name_sort,
            description_sort=i.description_sort,
            docket_numbers=i.docket_numbers,
            document_number=i.document_number,
            correction=i.correction,
            withdrawal=i.withdrawal,
        )
        link.citations.set([citations[pk] for pk in link.locations.objects.all().values_list("pk", flat=True)])
        link.subjects.set([subjects[pk] for pk in link.subjects.objects.all().values_list("pk", flat=True)])
        link.save()


def copy_internal_files(apps, schema_editor):


def copy_groups(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0034_v4_refactor_models'),
    ]

    operations = [
        migrations.RunPython(copy_public_categories),
        migrations.RunPython(copy_internal_categories),
        migrations.RunPython(copy_citations),
        migrations.RunPython(copy_subjects),
        migrations.RunPython(copy_public_links),
        migrations.RunPython(copy_federal_register_links),
        migrations.RunPython(copy_internal_files),
        migrations.RunPython(copy_groups),
    ]
