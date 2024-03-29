# Generated by Django 3.2.15 on 2022-08-18 11:08

from django.db import migrations


def populate_config_and_doctype(apps, schema_editor):
    FederalRegisterCategoryLink = apps.get_model("resources", "FederalRegisterCategoryLink")
    FederalRegisterDocument = apps.get_model("resources", "FederalRegisterDocument")
    Category = apps.get_model("resources", "Category")
    AbstractCategory = apps.get_model("resources", "AbstractCategory")
    ResourcesConfiguration = apps.get_model("resources", "ResourcesConfiguration")
    
    config = (ResourcesConfiguration.objects.create()
                if len(ResourcesConfiguration.objects.all()) < 1
                else ResourceConfiguration.objects.first())
    
    docs = FederalRegisterDocument.objects.all()
    if len(docs) < 1:
        return # only create FR doc category if we have existing docs in the database (i.e. in prod)

    if not config.fr_doc_category:
        try:
            category = AbstractCategory.objects.get(name="Federal Register Docs")
        except AbstractCategory.DoesNotExist:
            category = Category.objects.create(name="Federal Register Docs")
        config.fr_doc_category = category
        config.save()
    category = config.fr_doc_category

    for doc in FederalRegisterDocument.objects.all():
        try:
            value = FederalRegisterCategoryLink.objects.get(category=doc.category).name
        except FederalRegisterCategoryLink.DoesNotExist:
            value = ""

        if value == "Rule" or value == "Final Rules":
            doc.doc_type = "Final"
        elif value == "Proposed Rules" or value == "Proposed Rule":
            doc.doc_type = "NPRM"

        doc.category = category
        doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0021_frdoc_doc_type_and_config'),
    ]

    operations = [
        migrations.RunPython(populate_config_and_doctype),
    ]
