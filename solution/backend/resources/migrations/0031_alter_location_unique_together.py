# Generated by Django 3.2.18 on 2023-03-16 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0030_alter_location_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='location',
            unique_together={('type', 'title', 'part', 'subpart'), ('type', 'title', 'part', 'section')},
        ),
    ]
