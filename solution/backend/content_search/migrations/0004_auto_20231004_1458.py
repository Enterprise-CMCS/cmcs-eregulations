# Generated by Django 3.2.22 on 2023-10-04 14:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('file_manager', '0011_auto_20230925_1423'),
        ('content_search', '0003_auto_20231004_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentindex',
            name='file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='file_manager.uploadedfile'),
        ),
        migrations.DeleteModel(
            name='GenericContent',
        ),
    ]
