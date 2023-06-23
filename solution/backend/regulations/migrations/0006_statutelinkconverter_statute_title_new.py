# Generated by Django 3.2.19 on 2023-06-23 14:04

from django.db import migrations, models


roman_table = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}


def roman_to_int(roman):
    result = 0
    for i in range(len(roman) - 1, -1, -1):
        if roman[i] not in roman_table:
            return -1
        num = roman_table[roman[i]]
        result = result - num if 3 * num < result else result + num
    return result


def convert_roman_to_int(apps, schema_editor):
    StatuteLinkConverter = apps.get_model("regulations", "StatuteLinkConverter")
    for i in StatuteLinkConverter.objects.all():
        try:
            i.statute_title_new = int(i.statute_title)
        except ValueError:
            i.statute_title_new = roman_to_int(i.statute_title.upper().strip())
        i.save()


class Migration(migrations.Migration):

    dependencies = [
        ('regulations', '0005_auto_20230523_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='statutelinkconverter',
            name='statute_title_new',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.RunPython(convert_roman_to_int),
        migrations.RemoveField(
            model_name='statutelinkconverter',
            name='statute_title',
        ),
        migrations.RenameField(
            model_name='statutelinkconverter',
            old_name='statute_title_new',
            new_name='statute_title',
        ),
    ]
