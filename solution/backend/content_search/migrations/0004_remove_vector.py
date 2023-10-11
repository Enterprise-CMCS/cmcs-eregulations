

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('content_search', '0003_index_existing_items'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
              ALTER TABLE content_search_contentindex DROP COLUMN vector_column;
            '''
        ),
    ]
