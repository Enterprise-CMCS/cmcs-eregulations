# Contains custom fields for use throughout eRegs


import datetime
import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


def validate_date(value):
    # If a day is entered into the date field, validate for months with less than 31 days.
    if value and value.strip() != "":
        date_fields = value.strip().split("-")
        if len(date_fields) == 3:
            (year, month, day) = date_fields
            try:
                _ = datetime.date(int(year), int(month), int(day))
            except ValueError:
                raise ValidationError(f'{day} is not a valid day for the month of {month}.')


class VariableDateField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs = {**kwargs, **{
            "max_length": 10,
            "null": True,
            "blank": True,
            "help_text": "Leave blank or enter one of: \"YYYY\", \"YYYY-MM\", or \"YYYY-MM-DD\".",
            "validators": [
                validate_date,
                RegexValidator(
                    regex=r"^\d{4}((-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]))|(-(0[1-9]|1[0-2])))?$",
                    message="Date field must be blank or of the format \"YYYY\", \"YYYY-MM\", or \"YYYY-MM-DD\". "
                            "For example: 2021, 2021-01, or 2021-01-31.",
                ),
            ],
        }}
        return super().__init__(*args, **kwargs)


class NaturalSortField(models.CharField):
    def __init__(self, for_field, **kwargs):
        self.for_field = for_field
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('editable', False)
        kwargs.setdefault('max_length', 255)
        super(NaturalSortField, self).__init__(**kwargs)
        self.max_length = kwargs['max_length']

    def deconstruct(self):
        name, path, args, kwargs = super(NaturalSortField, self).deconstruct()
        args.append(self.for_field)
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        return self.naturalize(getattr(model_instance, self.for_field))

    def naturalize(self, string):
        def naturalize_int_match(match):
            return '%08d' % (int(match.group(0)),)
        if string:
            string = string.lower()
            string = string.strip()
            string = re.sub(r'\d+', naturalize_int_match, string)
            string = string[:self.max_length]

        return string
