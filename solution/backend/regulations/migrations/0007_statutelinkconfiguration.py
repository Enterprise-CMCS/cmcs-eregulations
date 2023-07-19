# Generated by Django 3.2.18 on 2023-07-12 16:12

from django.db import migrations, models
import django_jsonform.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('regulations', '0006_statutelinkconverter_statute_title_new'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatuteLinkConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link_statute_refs', models.BooleanField(default=True, help_text='Should eRegs link statutes of the form "Section 1902 of the Act" to house.gov?')),
                ('link_usc_refs', models.BooleanField(default=True, help_text='Should eRegs link statutes of the form "42 U.S.C. 123(a)" to house.gov?')),
                ('do_not_link', django_jsonform.models.fields.ArrayField(base_field=models.TextField(), blank=True, default=list, help_text='Regulation text that is listed here will not be automatically linked.', size=None)),
            ],
            options={
                'verbose_name': 'Statute Link Configuration',
            },
        ),
    ]
