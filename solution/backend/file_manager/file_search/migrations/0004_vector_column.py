

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('file_search', '0003_alter_fileindex_date_string'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
              ALTER TABLE file_search_fileindex ADD COLUMN vector_column tsvector GENERATED ALWAYS AS (
                setweight(to_tsvector('english', coalesce(doc_name_string, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(summary_string,'')), 'A') ||
                setweight(to_tsvector('english', coalesce(file_name_string,'')), 'C') ||
                setweight(to_tsvector('english', coalesce(subject_string,'')), 'B') ||
                setweight(to_tsvector('english', coalesce(doc_type_string,'')), 'B') ||
                setweight(to_tsvector('english', coalesce(date_string,'')), 'C') ||
                setweight(to_tsvector('english', coalesce(content,'')), 'D')
              ) STORED;
              CREATE INDEX file_search_index_vec ON file_search_fileindex USING GIN (vector_column);
            ''',

            reverse_sql = '''
              ALTER TABLE file_search_fileindex DROP COLUMN vector_column;
            '''
        ),
    ]
