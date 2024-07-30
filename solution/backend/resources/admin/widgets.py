from django.forms import ModelChoiceField
from django.utils.html import format_html


class CustomCategoryChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return format_html("&nbsp;&nbsp;&nbsp;&nbsp;{}", obj.name) if "Subcategory" in obj._meta.verbose_name else obj.name
