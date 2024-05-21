# Generated by Django 5.0.4 on 2024-05-21 14:41

import common.fields
import common.mixins
import django.core.validators
import django.db.models.deletion
import django_jsonform.models.fields
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0033_federalregisterdocument_raw_text_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractCitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.IntegerField()),
                ('part', models.IntegerField()),
                ('old_pk', models.IntegerField(null=True, unique=True)),
            ],
            bases=(models.Model, common.mixins.DisplayNameFieldMixin),
        ),
        migrations.CreateModel(
            name='NewAbstractCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True)),
                ('order', models.IntegerField(blank=True, default=0)),
                ('show_if_empty', models.BooleanField(default=False)),
            ],
            bases=(models.Model, common.mixins.DisplayNameFieldMixin),
        ),
        migrations.CreateModel(
            name='NewAbstractResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved', models.BooleanField(default=True, help_text='Documents will be visible on eRegulations to all authorized users once they are approved.')),
                ('cfr_citation_history', models.JSONField(default=list)),
                ('act_citations', common.fields.StatuteRefField(blank=True, default=list, verbose_name='Statute reference citations')),
                ('usc_citations', common.fields.UscRefField(blank=True, default=list, verbose_name='U.S.C. reference citations')),
                ('editor_notes', models.TextField(blank=True, help_text='Use this field to store notes meant for other editors. Notes in this field are not displayed outside this editing screen.')),
                ('document_id', models.CharField(blank=True, help_text='This is the citation number for the rule. It usually looks like this: "55 FR 10938", where "55" is the volume number and "10938" is the page number.', max_length=512, verbose_name='Document ID')),
                ('title', models.TextField(blank=True)),
                ('date', common.fields.VariableDateField(blank=True, help_text='Leave blank or enter the date the document was created or published. Some examples of valid dates are: "2024", "2024-01", or "2024-01-31".', max_length=10, null=True, validators=[common.fields.validate_date, django.core.validators.RegexValidator(message='Date field must be blank or of the format "YYYY", "YYYY-MM", or "YYYY-MM-DD". For example: 2021, 2021-01, or 2021-01-31.', regex='^\\d{4}((-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]))|(-(0[1-9]|1[0-2])))?$')])),
                ('url', models.URLField(blank=True, help_text='To link to an existing document - for example in Box or SharePoint - enter the full URL here.', max_length=512)),
                ('extract_url', models.URLField(blank=True, max_length=512)),
                ('document_id_sort', common.fields.NaturalSortField('document_id', db_index=True, editable=False, max_length=255, null=True)),
                ('title_sort', common.fields.NaturalSortField('title', db_index=True, editable=False, max_length=255, null=True)),
                ('category', models.ForeignKey(blank=True, help_text='Choose a single category or subcategory for the document. Choosing a subcategory will also apply the category when the document is listed.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resources', to='resources.newabstractcategory')),
                ('cfr_citations', models.ManyToManyField(blank=True, help_text='Select regulation citations related to this document. Hold down "Control", or "Command" on a Mac, to select more than one.', related_name='resources', to='resources.abstractcitation')),
            ],
            bases=(models.Model, common.mixins.DisplayNameFieldMixin),
        ),
        migrations.CreateModel(
            name='NewSubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=512)),
                ('short_name', models.CharField(blank=True, max_length=50)),
                ('abbreviation', models.CharField(blank=True, max_length=10)),
                ('description', models.TextField(blank=True)),
                ('combined_sort', common.fields.CombinedNaturalSort(['short_name', 'abbreviation', 'full_name'], db_index=True, editable=False, max_length=255, null=True)),
                ('old_pk', models.IntegerField(null=True, unique=True)),
            ],
            options={
                'verbose_name': 'Subject',
                'verbose_name_plural': 'Subjects',
            },
            bases=(models.Model, common.mixins.DisplayNameFieldMixin),
        ),
        migrations.CreateModel(
            name='NewSubpart',
            fields=[
                ('abstractcitation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.abstractcitation')),
                ('subpart_id', models.CharField(max_length=12)),
            ],
            options={
                'verbose_name': 'Subpart',
                'verbose_name_plural': 'Subparts',
                'ordering': ['title', 'part', 'subpart_id'],
            },
            bases=('resources.abstractcitation',),
        ),
        migrations.CreateModel(
            name='AbstractInternalCategory',
            fields=[
                ('newabstractcategory_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.newabstractcategory')),
                ('old_pk', models.IntegerField(null=True, unique=True)),
            ],
            bases=('resources.newabstractcategory',),
        ),
        migrations.CreateModel(
            name='AbstractPublicCategory',
            fields=[
                ('newabstractcategory_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.newabstractcategory')),
                ('old_pk', models.IntegerField(null=True, unique=True)),
            ],
            bases=('resources.newabstractcategory',),
        ),
        migrations.CreateModel(
            name='AbstractInternalResource',
            fields=[
                ('newabstractresource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.newabstractresource')),
                ('summary', models.TextField(blank=True, help_text='Write two or three sentences as a preview of the document for others.')),
                ('old_pk', models.IntegerField(null=True, unique=True)),
            ],
            bases=('resources.newabstractresource',),
        ),
        migrations.CreateModel(
            name='AbstractPublicResource',
            fields=[
                ('newabstractresource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.newabstractresource')),
                ('old_pk', models.IntegerField(null=True, unique=True)),
            ],
            bases=('resources.newabstractresource',),
        ),
        migrations.AddField(
            model_name='newabstractresource',
            name='subjects',
            field=models.ManyToManyField(blank=True, help_text='Select subjects related to this document. Hold down "Control", or "Command" on a Mac, to select more than one.', related_name='resources', to='resources.newsubject'),
        ),
        migrations.CreateModel(
            name='NewSection',
            fields=[
                ('abstractcitation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.abstractcitation')),
                ('section_id', models.IntegerField()),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='resources.newsubpart')),
            ],
            options={
                'verbose_name': 'Section',
                'verbose_name_plural': 'Sections',
                'ordering': ['title', 'part', 'section_id'],
            },
            bases=('resources.abstractcitation',),
        ),
        migrations.CreateModel(
            name='InternalCategory',
            fields=[
                ('abstractinternalcategory_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.abstractinternalcategory')),
                ('name', models.CharField(max_length=512, unique=True)),
            ],
            options={
                'verbose_name': 'Internal Category',
                'verbose_name_plural': 'Internal Categories',
                'ordering': ['order', 'name'],
            },
            bases=('resources.abstractinternalcategory',),
        ),
        migrations.CreateModel(
            name='PublicCategory',
            fields=[
                ('abstractpubliccategory_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.abstractpubliccategory')),
                ('name', models.CharField(max_length=512, unique=True)),
            ],
            options={
                'verbose_name': 'Public Category',
                'verbose_name_plural': 'Public Categories',
                'ordering': ['order', 'name'],
            },
            bases=('resources.abstractpubliccategory',),
        ),
        migrations.CreateModel(
            name='InternalFile',
            fields=[
                ('abstractinternalresource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.abstractinternalresource')),
                ('file_name', models.CharField(blank=True, editable=False, max_length=512)),
                ('file_type', models.CharField(blank=True, editable=False, max_length=32)),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False)),
            ],
            bases=('resources.abstractinternalresource',),
        ),
        migrations.CreateModel(
            name='InternalLink',
            fields=[
                ('abstractinternalresource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.abstractinternalresource')),
            ],
            bases=('resources.abstractinternalresource',),
        ),
        migrations.CreateModel(
            name='FederalRegisterLink',
            fields=[
                ('abstractpublicresource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.abstractpublicresource')),
                ('docket_numbers', django_jsonform.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=512), blank=True, default=list, size=None)),
                ('document_number', models.CharField(blank=True, help_text='This is a unique number for the rule that usually looks like "90-6614" and is listed at the very end of the rule.', max_length=255)),
                ('correction', models.BooleanField(default=False)),
                ('withdrawal', models.BooleanField(default=False)),
                ('action_type', models.CharField(blank=True, choices=[('RFI', 'RFI'), ('NPRM', 'NPRM'), ('Final', 'Final')], default='', max_length=32)),
            ],
            options={
                'verbose_name': 'Federal Register Link',
                'verbose_name_plural': 'Federal Register Links',
                'ordering': ['-date', 'document_number', 'document_id', 'title'],
            },
            bases=('resources.abstractpublicresource',),
        ),
        migrations.CreateModel(
            name='PublicLink',
            fields=[
                ('abstractpublicresource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.abstractpublicresource')),
            ],
            options={
                'verbose_name': 'Public Link',
                'verbose_name_plural': 'Public Links',
                'ordering': ['-date', 'document_id', 'title'],
            },
            bases=('resources.abstractpublicresource',),
        ),
        migrations.CreateModel(
            name='ResourceGroup',
            fields=[
                ('newabstractresource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.newabstractresource')),
                ('common_identifiers', django_jsonform.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=512), blank=True, default=list, help_text='Common identifiers to use when grouping resources. For example, when grouping Federal Register Documents, use the docket number prefix, like "CMS-1234-".', size=None)),
                ('resources', models.ManyToManyField(blank=True, related_name='resource_groups', to='resources.newabstractresource')),
            ],
            options={
                'verbose_name': 'Resource Group',
                'verbose_name_plural': 'Resource Groups',
                'ordering': ['document_id', 'common_identifiers'],
            },
            bases=('resources.newabstractresource',),
        ),
        migrations.CreateModel(
            name='InternalSubCategory',
            fields=[
                ('abstractinternalcategory_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.abstractinternalcategory')),
                ('name', models.CharField(max_length=512, unique=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='resources.internalcategory')),
            ],
            options={
                'verbose_name': 'Internal Subcategory',
                'verbose_name_plural': 'Internal Subcategories',
                'ordering': ['order', 'name'],
            },
            bases=('resources.abstractinternalcategory',),
        ),
        migrations.CreateModel(
            name='PublicSubCategory',
            fields=[
                ('abstractpubliccategory_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.abstractpubliccategory')),
                ('name', models.CharField(max_length=512, unique=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='resources.publiccategory')),
            ],
            options={
                'verbose_name': 'Public Subcategory',
                'verbose_name_plural': 'Public Subcategories',
                'ordering': ['order', 'name'],
            },
            bases=('resources.abstractpubliccategory',),
        ),
    ]
