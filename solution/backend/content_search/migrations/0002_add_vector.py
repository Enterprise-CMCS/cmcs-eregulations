

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('content_search', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
              ALTER TABLE content_search_contentindex ADD COLUMN vector_column tsvector GENERATED ALWAYS AS (
                setweight(to_tsvector('english', coalesce(doc_name_string, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(summary_string,'')), 'A') ||
                setweight(to_tsvector('english', coalesce(file_name_string,'')), 'C') ||
                setweight(to_tsvector('english', coalesce(date_string,'')), 'C') ||
                setweight(to_tsvector('english', coalesce(content,'')), 'D')
              ) STORED;
              CREATE INDEX content_search_index_vec ON content_search_contentindex USING GIN (vector_column);
            ''',

            reverse_sql = '''
              ALTER TABLE content_search_contentindex DROP COLUMN vector_column;
            '''
        ),
    ]
