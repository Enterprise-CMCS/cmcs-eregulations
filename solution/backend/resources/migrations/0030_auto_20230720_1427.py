# Generated by Django 3.2.19 on 2023-07-20 14:27

import common.fields
import django.core.validators
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0029_alter_federalregisterdocument_doc_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='federalregisterdocument',
            name='date',
            field=common.fields.VariableDateField(blank=True, help_text='Leave blank or enter one of: "YYYY", "YYYY-MM", or "YYYY-MM-DD".', max_length=10, null=True, validators=[common.fields.validate_date, django.core.validators.RegexValidator(message='Date field must be blank or of the format "YYYY", "YYYY-MM", or "YYYY-MM-DD". For example: 2021, 2021-01, or 2021-01-31.', regex='^\\d{4}((-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]))|(-(0[1-9]|1[0-2])))?$')]),
        ),
        migrations.AlterField(
            model_name='supplementalcontent',
            name='date',
            field=common.fields.VariableDateField(blank=True, help_text='Leave blank or enter one of: "YYYY", "YYYY-MM", or "YYYY-MM-DD".', max_length=10, null=True, validators=[common.fields.validate_date, django.core.validators.RegexValidator(message='Date field must be blank or of the format "YYYY", "YYYY-MM", or "YYYY-MM-DD". For example: 2021, 2021-01, or 2021-01-31.', regex='^\\d{4}((-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]))|(-(0[1-9]|1[0-2])))?$')]),
        ),
    ]
