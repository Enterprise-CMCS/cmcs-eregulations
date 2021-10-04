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

admin.site.register(SupplementalContent)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(SubSubCategory)
admin.site.register(Section)
admin.site.register(SubjectGroup)
admin.site.register(Subpart)
