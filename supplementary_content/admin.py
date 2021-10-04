from django.contrib import admin
from django.db.models.functions import Cast
from django.db.models import IntegerField, ManyToManyField
from django.contrib.admin.widgets import FilteredSelectMultiple

# Register your models here.

from .models import (
    SupplementalContent,
    Category,
    SubCategory,
    SubSubCategory,
    Section,
    SubjectGroup,
    Subpart,
)
from .filters import (
    TitleFilter,
    PartFilter,
    SectionFilter,
)

admin.register(SupplementalContent)
admin.register(Category)
admin.register(SubCategory)
admin.register(SubSubCategory)
admin.register(Section)
admin.register(SubjectGroup)
admin.register(Subpart)
