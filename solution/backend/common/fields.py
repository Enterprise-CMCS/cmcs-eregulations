# Contains custom fields for use throughout eRegs
import datetime
import re
from functools import partial

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django_jsonform.models.fields import JSONField
from drf_spectacular.utils import OpenApiTypes, extend_schema_field
from natsort import natsorted
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


# Begin Gemini code

# --- Core Logic Helpers (Adapted from natural_sort.py) ---

def split_natural_parts(s):
    """
    Splits a string into a list of number segments (kept as strings) and text segments.
    """
    if not isinstance(s, str):
        s = str(s)

    # The regex splits by sequences of digits but keeps the digits in the result.
    parts = re.split(r'(\d+)', s)
    # Filter out empty strings that result from the split (e.g., at the start/end)
    return [item for item in parts if item]


def natural_sort_key_builder(value: str, padding_length: int = 20) -> str:
    """
    Generates a single, highly sortable string key by zero-padding all number segments.

    Args:
        value: The string to be converted (e.g., '1860D-11').
        padding_length: The fixed width to pad numerical segments to.

    Returns:
        A single string (e.g., '1860D-00000000000000000011').
    """
    # 1. Split the value into natural parts
    parts = split_natural_parts(value)

    # 2. Process parts: pad numbers, keep text as is
    processed_parts = []
    for part in parts:
        # Check if the part is a digit sequence
        if part.isdigit():
            # Pad the number with leading zeros to the fixed length
            processed_parts.append(part.zfill(padding_length))
        else:
            # Keep text segments as is
            processed_parts.append(part)

    # 3. Join the processed parts into a single key string
    return "".join(processed_parts)

# --- Django Custom Field Implementation ---


class NaturalSortGeminiField(models.CharField):
    """
    A custom CharField that manages a hidden sort key column for natural ordering.

    The key is generated from:
    1. The field itself (default).
    2. An external field specified by the `source_field` argument.

    Usage Examples:

    # 1. Default (sorts by 'item_name')
    # Use 'item_name_key' for sorting
    class MyModel(models.Model):
        item_name = NaturalSortGeminiField(max_length=100)

    # 2. Explicit (sorts by 'item_code')
    # Use 'item_name_key' for sorting, which is derived from 'item_code'
    class MyOtherModel(models.Model):
        item_code = models.CharField(max_length=50)
        item_name = NaturalSortGeminiField(
            max_length=100,
            source_field='item_code'
        )
        # Note: In this case, 'item_name' would typically be editable=False
        # or used only for display.

    To sort naturally, use: MyModel.objects.all().order_by('item_name_key')
    """

    def __init__(self, *args, **kwargs):
        # New argument: the name of the model field to use as the source for the key calculation.
        self.source_field_name = kwargs.pop('source_field', None)

        # The internal sort key column will be a TextField
        self.sort_key_field = models.TextField(editable=False, null=True, blank=True)
        # Attribute name of the field this class is attached to (e.g., 'item_name')
        self.main_attname = None
        # Name for the hidden sort key column (e.g., 'item_name_key')
        self.sort_key_attname = None

        # Define the padding length for numbers in the sort key
        self.padding_length = kwargs.pop('padding_length', 20)

        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        # 1. Capture the attribute name of the field itself (e.g., 'item_name')
        self.main_attname = name

        # 2. Set the name for the hidden sort key column
        self.sort_key_attname = f'{name}_key'
        self.sort_key_field.attname = self.sort_key_attname
        self.sort_key_field.column = self.sort_key_attname

        # 3. Add the sort key field to the model
        cls.add_to_class(self.sort_key_attname, self.sort_key_field)

        # 4. Call the parent's contribution method for the main field
        super().contribute_to_class(cls, name, **kwargs)

    def pre_save(self, model_instance, add):
        """
        Called before the model is saved. Calculates the natural sort key and
        sets the value of the hidden field.
        """
        # Determine the source of the value for key generation.
        # Defaults to the field this class is attached to (self.main_attname).
        source_attname = self.source_field_name if self.source_field_name else self.main_attname

        # Retrieve the raw value from the model instance
        raw_value = getattr(model_instance, source_attname)

        # In default mode, we need the parent class to clean and validate the value
        # before we use it, but we MUST do this *after* retrieving the raw_value
        # if the source is external.
        if source_attname == self.main_attname:
            value = super().pre_save(model_instance, add)
        else:
            value = raw_value

        # Only proceed if the value is not None/empty
        if value:
            # Generate the padded sort key
            # Ensure value is a string before passing to key builder
            sort_key = natural_sort_key_builder(str(value), self.padding_length)
        else:
            sort_key = None

        # Set the generated key on the model instance's hidden field attribute
        setattr(model_instance, self.sort_key_attname, sort_key)

        # Return the value for the field's own column (what the parent CharField handles)
        # If we used an external source, the value of this field should be whatever
        # the user set, or None. We still call pre_save to get the cleaned result.
        return super().pre_save(model_instance, add) if source_attname != self.main_attname else value
# End Gemini code


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
