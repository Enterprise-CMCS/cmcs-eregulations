# Generated by Django 3.2.12 on 2022-03-30 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0003_auto_20220307_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='depth',
            field=models.IntegerField(default=3),
            preserve_default=False,
        ),
    ]
