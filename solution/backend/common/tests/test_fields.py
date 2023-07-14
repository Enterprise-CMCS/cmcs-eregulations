import unittest
from django.core.exceptions import ValidationError
from common.fields import VariableDateField



class VariableDateFieldTest(unittest.TestCase):
    def test_variable_date_field_valid(self):
        field = VariableDateField()
        value = "2022-07-15"
        try:
            field.clean(value, None)
        except ValidationError:
            self.fail(f"Validation error occurred for valid value: {value}")

    def test_variable_date_field_invalid(self):
        field = VariableDateField()
        value = "2022-02-30"  # Invalid day for February
        with self.assertRaises(ValidationError):
            field.clean(value, None)

    def test_variable_date_field_blank(self):
        field = VariableDateField(blank=True)
        value = ""
        try:
            field.clean(value, None)
        except ValidationError:
            self.fail("Validation error occurred for blank value")

    def test_variable_date_field_null(self):
        field = VariableDateField(null=True)
        value = None
        try:
            field.clean(value, None)
        except ValidationError:
            self.fail("Validation error occurred for null value")


if __name__ == '__main__':
    unittest.main()
