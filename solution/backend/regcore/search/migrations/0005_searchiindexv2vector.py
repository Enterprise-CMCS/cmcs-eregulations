

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('search', '0004_searchindexv2'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
              ALTER TABLE search_searchindexv2 ADD COLUMN vector_column tsvector GENERATED ALWAYS AS (
                setweight(to_tsvector('english', coalesce(section_string, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(title,'')), 'A') ||
                setweight(to_tsvector('english', coalesce(content,'')), 'B')
              ) STORED;
              CREATE INDEX search_index ON search_searchindexv2 USING GIN (vector_column);
            ''',

            reverse_sql = '''
              ALTER TABLE search_searchindexv2 DROP COLUMN vector_column;
            '''
        ),
    ]
