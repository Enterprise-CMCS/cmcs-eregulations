# Generated by Django 3.2.22 on 2023-10-30 08:13

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('content_search', '0002_add_vector'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentindex',
            name='uid',
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=36),
        ),
    ]
