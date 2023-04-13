# Generated by Django 3.2.18 on 2023-04-12 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0007_populate_index'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
                ALTER TABLE search_searchindexv2 DROP COLUMN vector_column;
            '''
        ),
        migrations.AlterField(
            model_name='searchindexv2',
            name='section_string',
            field=models.CharField(max_length=255),
        ),
        migrations.RunSQL(
            sql='''
              ALTER TABLE search_searchindexv2 ADD COLUMN vector_column tsvector GENERATED ALWAYS AS (
                setweight(to_tsvector('english', coalesce(section_string, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(section_title,'')), 'A') ||
                setweight(to_tsvector('english', coalesce(part_title,'')), 'A') ||
                setweight(to_tsvector('english', coalesce(content,'')), 'B')
              ) STORED;
              CREATE INDEX search_index ON search_searchindexv2 USING GIN (vector_column);
            ''',
        )
    ]
