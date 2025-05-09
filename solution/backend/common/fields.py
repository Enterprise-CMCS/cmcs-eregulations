# Contains custom fields for use throughout eRegs
import datetime
import re
from functools import partial

from natsort import natsorted

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django_jsonform.models.fields import JSONField
from drf_spectacular.utils import OpenApiTypes, extend_schema_field
from rest_framework import serializers

from .patterns import DASH_REGEX


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
            "blank": True,
            "help_text": "Leave blank or enter the date the document was created or published. "
                         "Some examples of valid dates are: \"2024\", \"2024-01\", or \"2024-01-31\".",
            "validators": [
                validate_date,
                RegexValidator(
                    regex=r"^\d{4}((-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]))|(-(0[1-9]|1[0-2])))?$",
                    message="Date field must be blank or of the format \"YYYY\", \"YYYY-MM\", or \"YYYY-MM-DD\". "
                            "For example: 2021, 2021-01, or 2021-01-31.",
                ),
            ],
        }}

        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        # Convert None to an empty string
        if value is None:
            value = ""
        return super().clean(value, model_instance)


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


#  Allows you to pass in an array of fields instead of just one.  It checks to see if the other fields are blank
#  To determine sorting, otherwise will do the same as natural sort field.
class CombinedNaturalSort(NaturalSortField):
    def pre_save(self, model_instance, add):
        for field in self.for_field:
            sort_attribute = getattr(model_instance, field)
            if sort_attribute:
                return self.naturalize(sort_attribute)


STATUTE_REF_SCHEMA = {
    "type": "list",
    "minItems": 0,
    "items": {
        "type": "dict",
        "keys": {
            "act": {
                "type": "string",
                "default": "Social Security Act",
                "placeholder": "Social Security Act",
                "required": True,
            },
            "section": {
                "type": "string",
                "required": True,
                "placeholder": "1902(a)(1)(C)",
            },
        },
    },
}


USC_REF_SCHEMA = {
    "type": "list",
    "minItems": 0,
    "items": {
        "type": "dict",
        "keys": {
            "title": {
                "type": "string",
                "required": True,
                "placeholder": "42",
            },
            "section": {
                "type": "string",
                "required": True,
                "placeholder": "1902(a)(1)(C)",
            },
        },
    },
}

CFR_REF_SCHEMA = {
    "type": "list",
    "minItems": 0,
    "items": {
        "type": "dict",
        "keys": {
            "title": {
                "type": "string",
                "required": True,
                "placeholder": "42",
            },
            "reference": {
                "type": "string",
                "required": True,
                "placeholder": "123.45(a)(1)",
            },
        },
    },
}


def _ref_field_pre_save_hook(value, schema):
    # Get names of keys from the schema
    keys = list(schema["items"]["keys"].keys())

    # Standardize dashes in the reference field and strip whitespace
    for i in value:
        i[keys[0]] = i[keys[0]].strip()
        i[keys[1]] = DASH_REGEX.sub("-", i[keys[1]].strip())

    # Return the naturally sorted list of references
    return natsorted(value, key=lambda x: (x[keys[0]], x[keys[1]]))


class _ReferenceField(JSONField):
    def __init__(self, schema, *args, **kwargs):
        kwargs = {**kwargs, **{
            "default": list,
            "blank": True,
            "pre_save_hook": partial(_ref_field_pre_save_hook, schema=schema),
            "schema": schema,
        }}
        super().__init__(*args, **kwargs)


class StatuteRefField(_ReferenceField):
    def __init__(self, *args, **kwargs):
        super().__init__(STATUTE_REF_SCHEMA, *args, **kwargs)


class UscRefField(_ReferenceField):
    def __init__(self, *args, **kwargs):
        super().__init__(USC_REF_SCHEMA, *args, **kwargs)


class CfrRefField(_ReferenceField):
    def __init__(self, *args, **kwargs):
        super().__init__(CFR_REF_SCHEMA, *args, **kwargs)


# Retrieves automatically generated search headlines
@extend_schema_field(OpenApiTypes.STR)
class HeadlineField(serializers.Field):
    def __init__(self, model_name=None, **kwargs):
        self.model_name = model_name
        kwargs["source"] = '*'
        kwargs["read_only"] = True
        if "blank_when_no_highlight" in kwargs:
            self.blank_when_no_highlight = kwargs["blank_when_no_highlight"]
            del kwargs["blank_when_no_highlight"]
        else:
            self.blank_when_no_highlight = False
        super().__init__(**kwargs)

    def to_representation(self, obj):
        text = getattr(obj, f"{self.model_name}_{self.field_name}", getattr(obj, self.field_name, None))
        if text and "<span class='search-highlight'>" not in text and self.blank_when_no_highlight:
            return None
        return text
