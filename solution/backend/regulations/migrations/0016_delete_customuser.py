# Generated by Django 5.0.6 on 2024-05-17 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('regulations', '0015_customuser'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]