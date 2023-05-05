# Generated by Django 3.2.18 on 2023-05-02 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0028_set_name_sort'),
    ]

    operations = [
        migrations.AlterField(
            model_name='federalregisterdocument',
            name='doc_type',
            field=models.CharField(blank=True, choices=[('RFI', 'RFI'), ('NPRM', 'NPRM'), ('Final', 'Final')], default='', max_length=255),
        ),
    ]
