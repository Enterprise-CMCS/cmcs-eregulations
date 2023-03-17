from django.db import migrations
import resources.models
import re


def migrate_locations(apps, schema_editor):
    Section = apps.get_model("resources", "Section")
    Subpart = apps.get_model("resources", "Subpart")
    Location = apps.get_model("resources", "Location")

    for i in Subpart.objects.all():
        Location.objects.create(
            type=1,
            title=i.title,
            part=i.part,
            subpart=i.subpart_id,
        )

    for i in Section.objects.all():
        try:
            if i.parent:
                parent = Location.objects.get(
                    type=1,
                    title=i.parent.title,
                    part=i.parent.part,
                    subpart=i.parent.subpart.subpart_id,
                )
            else:
                parent = None
        except Location.DoesNotExist:
            parent = None

        Location.objects.create(
            type=0,
            title=i.title,
            part=i.part,
            section=i.section_id,
            parent=parent,
        )


def migrate_categories(apps, schema_editor):
    Category = apps.get_model("resources", "Category")
    SubCategory = apps.get_model("resources", "SubCategory")
    NewCategory = apps.get_model("resources", "NewCategory")

    for i in Category.objects.all():
        NewCategory.objects.create(
            type=0,
            name=i.name,
            description=i.description,
            order=i.order,
            show_if_empty=i.show_if_empty,
        )
    
    for i in SubCategory.objects.all():
        try:
            if i.parent:
                parent = NewCategory.objects.get(
                    type=0,
                    name=i.parent.name,
                    description=i.parent.description,
                    order=i.parent.order,
                    show_if_empty=i.parent.show_if_empty,
                )
            else:
                parent = None
        except NewCategory.DoesNotExist:
            parent = None

        NewCategory.objects.create(
            type=1,
            name=i.name,
            description=i.description,
            order=i.order,
            show_if_empty=i.show_if_empty,
            parent=parent,
        )


def migrate_groups(apps, schema_editor):
    ResourceGroup = apps.get_model("resources", "ResourceGroup")
    FederalRegisterDocumentGroup = apps.get_model("resources", "FederalRegisterDocumentGroup")
    for i in FederalRegisterDocumentGroup.objects.all():
        ResourceGroup.objects.create(
            type=0,
            docket_number_prefixes=i.docket_number_prefixes,
        )


def migrate_supplemental_content(apps, schema_editor):
    SupplementalContent = apps.get_model("resources", "SupplementalContent")
    Resource = apps.get_model("resources", "Resource")
    NewCategory = apps.get_model("resources", "NewCategory")
    Location = apps.get_model("resources", "Location")

    for i in SupplementalContent.objects.all():
        # find matching category
        try:
            if i.category:
                category = NewCategory.objects.get(
                    name=i.category.name,
                    description=i.category.description,
                    order=i.category.order,
                    show_if_empty=i.category.show_if_empty,
                )
            else:
                category = None
        except NewCategory.DoesNotExist:
            category = None

        # find locations
        locations = []
        for section in i.locations.filter(section__isnull=False):
            try:
                locations.append(Location.objects.get(
                    type=0,
                    title=section.title,
                    part=section.part,
                    section=section.section.section_id,
                ))
            except Location.DoesNotExist:
                pass
        for subpart in i.locations.filter(subpart__isnull=False):
            try:
                locations.append(Location.objects.get(
                    type=1,
                    title=subpart.title,
                    part=subpart.part,
                    subpart=subpart.subpart.subpart_id,
                ))
            except Location.DoesNotExist:
                pass

        resource = Resource.objects.create(
            type=0,
            created_at=i.created_at,
            updated_at=i.updated_at,
            approved=i.approved,
            category=category,
            location_history=i.location_history,
            name=i.name,
            description=i.description,
            url=i.url,
            internal_notes=i.internal_notes,
            date=i.date,
            name_sort=i.name_sort,
            description_sort=i.description_sort
        )
        resource.locations.set(locations)
        resource.save()


def migrate_federal_register_documents(apps, schema_editor):
    FederalRegisterDocument = apps.get_model("resources", "FederalRegisterDocument")
    Resource = apps.get_model("resources", "Resource")
    NewCategory = apps.get_model("resources", "NewCategory")
    Location = apps.get_model("resources", "Location")
    FederalRegisterDocumentGroup = apps.get_model("resources", "FederalRegisterDocumentGroup")
    ResourceGroup = apps.get_model("resources", "ResourceGroup")

    for i in FederalRegisterDocument.objects.all():
        # find matching category
        try:
            if i.category:
                category = NewCategory.objects.get(
                    name=i.category.name,
                    description=i.category.description,
                    order=i.category.order,
                    show_if_empty=i.category.show_if_empty,
                )
            else:
                category = None
        except NewCategory.DoesNotExist:
            category = None

        # find locations
        locations = []
        for section in i.locations.filter(section__isnull=False):
            try:
                locations.append(Location.objects.get(
                    type=0,
                    title=section.title,
                    part=section.part,
                    section=section.section.section_id,
                ))
            except Location.DoesNotExist:
                pass
        for subpart in i.locations.filter(subpart__isnull=False):
            try:
                locations.append(Location.objects.get(
                    type=1,
                    title=subpart.title,
                    part=subpart.part,
                    subpart=subpart.subpart.subpart_id,
                ))
            except Location.DoesNotExist:
                pass

        # find group
        if i.group:
            try:
                group = ResourceGroup.objects.get(
                    type=0,
                    docket_number_prefixes=i.group.docket_number_prefixes,
                )
            except ResourceGroup.DoesNotExist:
                group = None
        else:
            group = None

        resource = Resource.objects.create(
            type=1,
            created_at=i.created_at,
            updated_at=i.updated_at,
            approved=i.approved,
            category=category,
            location_history=i.location_history,
            name=i.name,
            description=i.description,
            url=i.url,
            internal_notes=i.internal_notes,
            date=i.date,
            name_sort=i.name_sort,
            description_sort=i.description_sort,
            group=group,
            docket_numbers=i.docket_numbers,
            document_number=i.document_number,
            correction=i.correction,
            withdrawal=i.withdrawal,
            doc_type=i.doc_type,
        )
        resource.locations.set(locations)
        resource.save()


def resolve_related_resources(apps, schema_editor):
    Resource = apps.get_model("resources", "Resource")
    for doc in Resource.objects.filter(type=1):
        if doc.group:
            doc.related_resources.set(doc.group.resources.exclude(id=doc.id).order_by("-date"))
            doc.save()


def migrate_resources_config(apps, schema_editor):
    ResourcesConfiguration = apps.get_model("resources", "ResourcesConfiguration")
    NewResourcesConfiguration = apps.get_model("resources", "NewResourcesConfiguration")
    NewCategory = apps.get_model("resources", "NewCategory")

    old_config = ResourcesConfiguration.objects.first()

    if old_config.fr_doc_category:
        # find category
        try:
            category = NewCategory.objects.get(
                name=old_config.fr_doc_category.name,
                description=old_config.fr_doc_category.description,
                order=old_config.fr_doc_category.order,
                show_if_empty=old_config.fr_doc_category.show_if_empty,
            )
        except NewCategory.DoesNotExist:
            category = None
    else:
        category = None

    NewResourcesConfiguration.objects.create(fr_doc_category=category)


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0029_location_newcategory_newcategorycategory_newcategorysubcategory_newfederalregisterdocument_newfedera'),
    ]

    operations = [
        migrations.RunPython(migrate_locations),
        migrations.RunPython(migrate_categories),
        migrations.RunPython(migrate_groups),
        migrations.RunPython(migrate_supplemental_content),
        migrations.RunPython(migrate_federal_register_documents),
        migrations.RunPython(resolve_related_resources),
        migrations.RunPython(migrate_resources_config),
    ]
