# Generated by Django 3.2.12 on 2022-02-17 16:11

from itertools import chain 

from django.db import migrations, models
import django.db.models.deletion


def create_parents(apps, schema_editor):
    AbstractModel = apps.get_model("supplemental_content", "AbstractModel")
    AbstractCategory = apps.get_model("supplemental_content", "AbstractCategory")
    AbstractLocation = apps.get_model("supplemental_content", "AbstractLocation")
    AbstractSupplementalContent = apps.get_model("supplemental_content", "AbstractSupplementalContent")

    for child in chain(AbstractCategory.objects.all(), AbstractLocation.objects.all(), AbstractSupplementalContent.objects.all()):
        parent = AbstractModel.objects.create()
        child.abstractmodel_ptr = parent.pk
        child.save()


def resave_all(apps, schema_editor):
    try:
        from supplemental_content.models import AbstractModel
        for model in AbstractModel.objects.all():
            model.save()
    except: # Primarily ImportError but safer to catch everything
        pass # Skip in case model is changed, renamed, or deleted in the future


class Migration(migrations.Migration):

    dependencies = [
        ('supplemental_content', '0011_auto_20220211_1139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='abstractlocation',
            name='display_name',
        ),
        migrations.CreateModel(
            name='AbstractModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(max_length=128, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='abstractcategory',
            name='abstractmodel_ptr',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='abstractlocation',
            name='abstractmodel_ptr',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='abstractsupplementalcontent',
            name='abstractmodel_ptr',
            field=models.IntegerField(null=True),
        ),
        migrations.RunPython(create_parents),
        migrations.RemoveField(
            model_name='abstractcategory',
            name='id',
        ),
        migrations.AlterField(
            model_name='abstractcategory',
            name='abstractmodel_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supplemental_content.abstractmodel'),
        ),
        migrations.RemoveField(
            model_name='abstractlocation',
            name='id',
        ),
        migrations.AlterField(
            model_name='abstractlocation',
            name='abstractmodel_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supplemental_content.abstractmodel'),
        ),
        migrations.RemoveField(
            model_name='abstractsupplementalcontent',
            name='id',
        ),
        migrations.AlterField(
            model_name='abstractsupplementalcontent',
            name='abstractmodel_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supplemental_content.abstractmodel'),
        ),
        migrations.RunPython(resave_all),
    ]
