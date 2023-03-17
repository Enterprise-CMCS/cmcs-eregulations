import json
import re

from django.contrib import admin
from django.contrib.admin.sites import site
from django.apps import apps
from django.urls import path
from django.db.models import Prefetch, Count
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.urls import reverse
from solo.admin import SingletonModelAdmin
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.forms.widgets import Textarea

# Register your models here.


from .filters import (
    TitleFilter,
    PartFilter,
    SectionFilter,
    SubpartFilter,
)

#from .serializers.locations import AbstractLocationPolymorphicSerializer
from . import actions

from common.admin import NewBaseAdmin


from .models import (
    Location,
    Section,
    Subpart,
    BaseCategory,
    Category,
    SubCategory,
    ResourceGroup,
    FederalRegisterDocumentGroup,
    Resource,
    SupplementalContent,
    FederalRegisterDocument,
)


class HiddenTypeFieldMixin:
    def get_fieldsets(self, request, obj=None):
        return [
            [None, {
                'classes': ['empty-form',],
                'fields': ['type',],
            }],
            [None, {
                'fields': self.shown_fields,
            }],
        ]


class NewLocationAdmin(NewBaseAdmin):
    readonly_fields = ("linked_resources",)

    def linked_resources(self, obj):
        display_text = "".join([
                                 "<a href={}>{}</a><br>".format(
                                  reverse('admin:{}_{}_change'.format("resources", type(child).__name__.lower()),
                                          args=(child.id,)), str(child))
                                 for child in obj.resources.all()])
        if display_text:
            return mark_safe(display_text)
        return "-"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("resources", Resource.objects.all()),
        )


@admin.register(Section)
class SectionAdmin(HiddenTypeFieldMixin, NewLocationAdmin):
    admin_priority = 40
    list_display = ("title", "part", "section", "parent")
    search_fields = ("title", "part", "section")
    ordering = ("title", "part", "section", "parent")
    shown_fields = ("title", "part", "section", "parent", "linked_resources")
    foreignkey_lookups = {
        "parent": lambda: Subpart.objects.all(),
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("parent", Subpart.objects.all()),
        )


@admin.register(Subpart)
class SubpartAdmin(HiddenTypeFieldMixin, NewLocationAdmin):
    admin_priority = 50
    list_display = ("title", "part", "subpart")
    search_fields = ("title", "part", "subpart")
    ordering = ("title", "part", "subpart")
    shown_fields = ("title", "part", "subpart", "linked_resources")


@admin.register(Category)
class CategoryAdmin(HiddenTypeFieldMixin, NewBaseAdmin):
    admin_priority = 10
    list_display = ("name", "description", "order", "show_if_empty")
    search_fields = ("name", "description")
    shown_fields = ("name", "description", "order", "show_if_empty")


@admin.register(SubCategory)
class SubCategoryAdmin(HiddenTypeFieldMixin, NewBaseAdmin):
    admin_priority = 20
    list_display = ("name", "description", "order", "show_if_empty", "parent")
    shown_fields = ("name", "description", "order", "show_if_empty", "parent")
    foreignkey_lookups = {
        "parent": lambda: Category.objects.all(),
    }


class FederalRegisterDocumentGroupForm(forms.ModelForm):
    resources = forms.ModelMultipleChoiceField(
        queryset=FederalRegisterDocument.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name="Documents",
            is_stacked=False,
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["resources"].initial = self.instance.resources.all()

    def save(self, commit=True):
        group = super().save(commit=False)
        group.save()
        group.resources.set(self.cleaned_data["resources"])
        group.save()
        return group

    class Meta:
        model = FederalRegisterDocumentGroup
        fields = ("type", "docket_number_prefixes", "resources")
        widgets = {
            "type": forms.HiddenInput(),
        }


@admin.register(FederalRegisterDocumentGroup)
class FederalRegisterDocumentGroupAdmin(NewBaseAdmin):
    form = FederalRegisterDocumentGroupForm
    admin_priority = 250
    list_display = ("docket_number_prefixes", "number_of_documents")
    list_display_links = ("docket_number_prefixes", "number_of_documents")
    search_fields = ["docket_number_prefixes"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(number_of_documents=Count("resources"))

    def number_of_documents(self, obj):
        return obj.number_of_documents


# @admin.register(ResourcesConfiguration)
# class ResourcesConfigurationAdmin(SingletonModelAdmin):
#     admin_priority = 0

#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "fr_doc_category":
#             kwargs["queryset"] = AbstractCategory.objects.all().select_subclasses()
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ResourceAdmin(NewBaseAdmin):
    actions = [actions.mark_approved, actions.mark_not_approved]
    filter_horizontal = ("locations",)
    admin_priority = 0
    empty_value_display = "NONE"
    ordering = ("-updated_at", "-date", "name", "category", "-created_at")

    list_filter = [
        "approved",
        TitleFilter,
        PartFilter,
        SectionFilter,
        SubpartFilter,
    ]

    foreignkey_lookups = {
        "category": lambda: BaseCategory.objects.all(),
    }

    manytomany_lookups = {
        "locations": lambda: Location.objects.all(),
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("category", BaseCategory.objects.all()),
        )

    # Overrides the save method in django admin to handle many to many relationships.
    # Looks at the locations added in bulk uploads and adds them if allowed, sends error message if not.
    def save_related(self, request, form, formsets, change):
        # Compute diff of selected and saved locations for the changelog
        selection = form.cleaned_data["locations"]
        saved_locations = list(form.instance.locations.all())
        additions = [AbstractLocationPolymorphicSerializer(x).data for x in selection if x not in saved_locations]
        removals = [AbstractLocationPolymorphicSerializer(x).data for x in saved_locations if x not in selection]

        bulk_locations = form.cleaned_data.get("bulk_locations")
        bulk_title = form.cleaned_data.get("bulk_title")
        bad_locations = []
        bulk_adds = []

        super().save_related(request, form, formsets, change)
        if bulk_locations:
            split_locations = bulk_locations.split(",")
            for location in split_locations:
                a = self.build_location(location.strip(), bulk_title)
                if a:
                    form.instance.locations.add(a.abstractlocation_ptr)
                    bulk_adds.append(AbstractLocationPolymorphicSerializer(a).data)
                else:
                    bad_locations.append(location)
            if bad_locations:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "The following locations were not added %s" % ((", ").join(bad_locations))
                )

        # Create and append changelog object, if any location changes occured
        if additions or removals or bulk_adds:
            form.instance.location_history.append({
                "user": str(request.user),
                "date": str(timezone.now()),
                "additions": additions,
                "removals": removals,
                "bulk_adds": bulk_adds,
            })
            form.instance.save()

    # Checks the location for the formats.
    # Valid sections: 42 433.1, 42 CFR 433.1, 42 433 1
    # Valid subparts: 42 433.A, 42 CFR 433 Subpart A, 42 CFR 433.A, 42 433 A
    # All inputs can have no title (i.e. 433.1 instead of 42 CFR 433.1, etc.)
    def build_location(self, location, default_title):
        section_regex = r"^(?:([0-9]+)\s+(?:cfr)?(?:\s+)?)?([0-9]+)(?:[\s]+|[.])([0-9]+)$"
        subpart_regex = r"^(?:([0-9]+)\s+(?:cfr)?(?:\s+)?)?([0-9]+)(?:\.|\s+(?:subpart\s+)?)((?!subpart)[a-z]+)$"
        section_search = re.search(section_regex, location.lower())
        subpart_search = re.search(subpart_regex, location.lower())

        if section_search:
            title, part, section = section_search.groups()
            title = default_title if not title else title
            if self.check_values(title, part, section, ""):
                try:
                    return Section.objects.get(
                        title=title,
                        part=part,
                        section_id=section,
                    )
                except Section.DoesNotExist:
                    return None
        elif subpart_search:
            title, part, subpart = subpart_search.groups()
            title = default_title if not title else title
            subpart = subpart.upper()
            if self.check_values(title, part, "", subpart):
                try:
                    return Subpart.objects.get(
                        title=title,
                        part=part,
                        subpart_id=subpart,
                    )
                except Subpart.DoesNotExist:
                    return None
        return None

    # Makes sure each value is the correct format for querying the locations
    def check_values(self, title, part, section, subpart):
        if not title.isdigit() or not part.isdigit():
            return False
        if section != "" and not section.isdigit():
            return False
        if subpart != "" and not isinstance(subpart, str):
            return False
        return True


class LocationHistoryWidget(Textarea):
    def locations_to_strings(self, locations):
        strings = []
        for i in locations:
            key = f"{i['type']}_id"
            strings.append(f"{i['title']} CFR {i['part']}.{i[key]}")
        if not strings:
            return None
        if len(strings) == 1:
            return strings[0]
        return ", ".join(strings[0:-1]) + ("," if len(strings) > 2 else "") + f" and {strings[-1]}"

    def format_value(self, value):
        try:
            output = []
            data = json.loads(value)
            if not data:
                return ""
            for i in range(len(data)):
                row = data[i]
                additions = self.locations_to_strings(row["additions"])
                removals = self.locations_to_strings(row["removals"])
                bulk_adds = self.locations_to_strings(row["bulk_adds"])
                date = parse_datetime(row["date"]).strftime("%Y-%m-%d at %I:%M %p")
                output.append(f"{i+1}: On {date}, {row['user']} %s%s%s%s%s." % (
                    f"added {additions}" if additions else "",
                    " and " if additions and removals else "",
                    f"removed {removals}" if removals else "",
                    " and " if (additions or removals) and bulk_adds else "",
                    f"bulk added {bulk_adds}" if bulk_adds else "",
                ))
            return "\n".join(output)
        except Exception:
            return "Can't render location history."


class ResourceForm(forms.ModelForm):
    bulk_title = forms.CharField(required=False, help_text="If bulk locations is missing a title, add it here.")
    bulk_locations = forms.CharField(
                        widget=forms.Textarea,
                        required=False,
                        help_text=mark_safe("Add a list of locations separated by a comma.  " +
                                            "ex. 42 430.10, 42 430 Subpart B, 45 18.150 " +
                                            "<a href='https://docs.google.com/document/d/1HKjg5pUQn" +
                                            "RP98i9xbGy0fPiGq_0a6p2PRXhwuDbmiek/edit#' " +
                                            "target='blank'>Click here for detailed documentation.</a>"))
    location_history = forms.JSONField(
                        widget=LocationHistoryWidget(attrs={"rows": 10, "cols": 120}),
                        required=False,
                        disabled=True)


@admin.register(SupplementalContent)
class SupplementalContentAdmin(ResourceAdmin):
    form = ResourceForm
    list_display = ("date", "name", "description", "category", "updated_at", "approved", "name_sort")
    list_display_links = ("date", "name", "description", "category", "updated_at")
    search_fields = ["date", "name", "description"]
    fields = ("approved", "name", "description", "date", "url", "category",
              "locations", "bulk_title", "bulk_locations", "internal_notes", "location_history")


@admin.register(FederalRegisterDocument)
class FederalRegisterDocumentAdmin(ResourceAdmin):
    form = ResourceForm
    list_display = ("date", "name", "description", "in_group", "docket_numbers",
                    "document_number", "category", "doc_type", "updated_at", "approved")
    list_display_links = ("date", "name", "description", "in_group", "docket_numbers",
                          "document_number", "category", "doc_type", "updated_at")
    search_fields = ["date", "name", "description", "docket_numbers", "document_number"]
    fields = ("approved", "docket_numbers", "group", "document_number", "name", "correction",
              "withdrawal", "description", "date", "url", "category", "doc_type", "locations",
              "bulk_title", "bulk_locations", "internal_notes", "location_history")

    def in_group(self, obj):
        group = str(obj.group)
        return group[0:20] + "..." if len(group) > 20 else group

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("group", FederalRegisterDocumentGroup.objects.all()),
        )

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + (("doc_type",) if obj else ())  # prevent changing name field on existing objects
