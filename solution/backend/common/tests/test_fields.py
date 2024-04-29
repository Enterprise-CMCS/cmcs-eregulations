import unittest

import pytest
from django.core.exceptions import ValidationError

from common.fields import HeadlineField, VariableDateField
from file_manager.models import Subject


class VariableDateFieldTest(unittest.TestCase):
    def setUp(self):
        self.field = VariableDateField()

    def test_valid_date_values(self):
        values = [
            "2022-07-15",
            "2022-07",
            "2022",
            "",
            None,
        ]
        for value in values:
            self.assertEqual(self.field.clean(value, value), value)

    def test_invalid_date_values(self):
        values = [
            {
                "value": "abcd-07",
                "error_message": "Date field must be blank or of the format \"YYYY\", \"YYYY-MM\", or \"YYYY-MM-DD\"",
            },
            {
                "value": "13",
                "error_message": "Date field must be blank or of the format \"YYYY\", \"YYYY-MM\", or \"YYYY-MM-DD\"",
            },
            {
                "value": "2022-02-30",
                "error_message": "30 is not a valid day for the month of 02.",
            },
        ]

        for value in values:
            with self.assertRaises(ValidationError) as context:
                self.field.clean(value["value"], None)
            self.assertIn(
                value["error_message"],
                str(context.exception),
            )


class HeadlineFieldTest(unittest.TestCase):
    def test_with_highlight(self):
        value = "hello <span class='search-highlight'>world</span>"

        def fake_obj():
            return None

        fake_obj.test_field = value

        field = HeadlineField()
        field.field_name = "test_field"
        self.assertEqual(field.to_representation(fake_obj), value)

        field = HeadlineField(blank_when_no_highlight=True)
        field.field_name = "test_field"
        self.assertEqual(field.to_representation(fake_obj), value)

    def test_without_highlight(self):
        value = "hello world"

        def fake_obj():
            return None

        fake_obj.test_field = value

        field = HeadlineField()
        field.field_name = "test_field"
        self.assertEqual(field.to_representation(fake_obj), value)

        field = HeadlineField(blank_when_no_highlight=True)
        field.field_name = "test_field"
        self.assertEqual(field.to_representation(fake_obj), None)


def clean_up():
    Subject.objects.all().delete()


def set_up_subjects():
    clean_up()
    Subject.objects.get_or_create(full_name="3test_subject_full", short_name="2test_subject_short", abbreviation='1abvr')


@pytest.mark.django_db
def test_combined_sort():
    set_up_subjects()
    s = Subject.objects.first()
    assert s.combined_sort == '00000002test_subject_short'
    s.short_name = ''
    s.save()
    s = Subject.objects.first()
    assert s.combined_sort == '00000001abvr'
    s.abbreviation = ''
    s.save()
    s = Subject.objects.first()
    assert s.combined_sort == '00000003test_subject_full'


if __name__ == '__main__':
    unittest.main()
