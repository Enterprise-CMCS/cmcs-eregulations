# Generated by Django 3.2.20 on 2023-08-28 11:34

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('file_manager', '0002_auto_20230828_1122'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='uploadcategory',
            options={'verbose_name_plural': 'Upload Categories'},
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
