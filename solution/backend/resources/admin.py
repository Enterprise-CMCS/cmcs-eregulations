import csv
import json
import re

from django import forms
from django.apps import apps
from django.contrib import admin, messages
from django.contrib.admin.sites import site
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import (
    Case,
    Count,
    F,
    Prefetch,
    Value,
    When,
)
from django.forms.widgets import Textarea
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.safestring import mark_safe
from solo.admin import SingletonModelAdmin

from content_search.functions import add_to_index

from . import actions
from .filters import (
    PartFilter,
    SectionFilter,
    SubpartFilter,
    TitleFilter,
)
from .models import (
    AbstractCategory,
    AbstractLocation,
    AbstractResource,
    Category,
    FederalRegisterDocument,
    FederalRegisterDocumentGroup,
    ResourcesConfiguration,
    Section,
    SubCategory,
    Subpart,
    SupplementalContent,
)
from .serializers.locations import AbstractLocationPolymorphicSerializer


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 200
    admin_priority = 20

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        lookups = getattr(self, "foreignkey_lookups", {})
        if db_field.name in lookups:
            kwargs["queryset"] = lookups[db_field.name]()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        lookups = getattr(self, "manytomany_lookups", {})
        if db_field.name in lookups:
            kwargs["queryset"] = lookups[db_field.name]()
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(ResourcesConfiguration)
class ResourcesConfigurationAdmin(SingletonModelAdmin):
    admin_priority = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "fr_doc_category":
            kwargs["queryset"] = AbstractCategory.objects.all().select_subclasses()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class LocationAdmin(BaseAdmin):
    readonly_fields = ("linked_resources",)

    def linked_resources(self, obj):
        display_text = "".join([
                                 "<a href={}>{}</a><br>".format(
                                  reverse('admin:{}_{}_change'.format("resources", type(child).__name__.lower()),
                                          args=(child.id,)), str(child))
                                 for child in obj.resources.all()])
        if display_text:
            return mark_safe(display_text)  # noqa: S308
        return "-"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("resources", AbstractResource.objects.all().select_subclasses()),
        )


@admin.register(Section)
class SectionAdmin(LocationAdmin):
    admin_priority = 40
    list_display = ("title", "part", "section_id", "parent")
    search_fields = ["title", "part", "section_id"]
    ordering = ("title", "part", "section_id", "parent")
    fields = ("title", "part", "section_id", "parent", "linked_resources")
    foreignkey_lookups = {
        "parent": lambda: Subpart.objects.all(),
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("parent", AbstractLocation.objects.all().select_subclasses()),
        )


@admin.register(Subpart)
class SubpartAdmin(LocationAdmin):
    admin_priority = 50
    list_display = ("title", "part", "subpart_id")
    search_fields = ["title", "part", "subpart_id"]
    ordering = ("title", "part", "subpart_id")
    fields = ("title", "part", "subpart_id", "linked_resources")


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    admin_priority = 10
    list_display = ("name", "description", "order", "show_if_empty")
    search_fields = ["name", "description"]
    ordering = ("name", "description", "order")


@admin.register(SubCategory)
class SubCategoryAdmin(CategoryAdmin):
    admin_priority = 20
    list_display = ("name", "description", "order", "show_if_empty", "parent")
    ordering = ("name", "description", "order", "parent")


class AbstractResourceAdmin(BaseAdmin):
    actions = [actions.mark_approved, actions.mark_not_approved]
    filter_horizontal = ("locations", "subjects")
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
        "category": lambda: AbstractCategory.objects.all().select_subclasses(),
    }

    manytomany_lookups = {
        "locations": lambda: AbstractLocation.objects.all().select_subclasses(),
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("category", AbstractCategory.objects.all().select_subclasses()),
        )

    def get_bulk_locations(self, bulk_locations, bulk_title=""):
        bulk_adds = []
        bad_locations = []
        split_locations = bulk_locations.split(",")
        for location in split_locations:
            a = self.build_location(location.strip(), bulk_title)
            if a:
                bulk_adds.append(a)
            else:
                bad_locations.append(location)
        return bulk_adds, bad_locations

    # Overrides the save method in django admin to handle many to many relationships.
    # Looks at the locations added in bulk uploads and adds them if allowed, sends error message if not.
    def save_related(self, request, form, formsets, change):
        # Compute diff of selected and saved locations for the changelog
        selection = form.cleaned_data["locations"]
        saved_locations = list(form.instance.locations.all().select_subclasses())
        additions = [AbstractLocationPolymorphicSerializer(x).data for x in selection if x not in saved_locations]
        removals = [AbstractLocationPolymorphicSerializer(x).data for x in saved_locations if x not in selection]

        bulk_locations = form.cleaned_data.get("bulk_locations")
        bulk_title = form.cleaned_data.get("bulk_title")
        bad_locations = []
        bulk_adds = []
        bulk_locs = []

        super().save_related(request, form, formsets, change)
        if bulk_locations:
            bulk_adds, bad_locations = self.get_bulk_locations(bulk_locations, bulk_title)
            if bad_locations:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "The following locations were not added %s" % ((", ").join(bad_locations))
                )
            if bulk_adds:
                for location in bulk_adds:
                    form.instance.locations.add(location.abstractlocation_ptr)
                    bulk_locs.append(AbstractLocationPolymorphicSerializer(location).data)
        # Create and append changelog object, if any location changes occured
        if additions or removals or bulk_adds:
            form.instance.location_history.append({
                "user": str(request.user),
                "date": str(timezone.now()),
                "additions": additions,
                "removals": removals,
                "bulk_adds": bulk_locs,
            })
            form.instance.save()
            add_to_index(form.instance)

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
                output.append(f"{i + 1}: On {date}, {row['user']} %s%s%s%s%s." % (
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
                        help_text=mark_safe("Add a list of locations separated by a comma.  " +  # noqa: S308
                                            "ex. 42 430.10, 42 430 Subpart B, 45 18.150 " +
                                            "<a href='https://docs.google.com/document/d/1HKjg5pUQn" +
                                            "RP98i9xbGy0fPiGq_0a6p2PRXhwuDbmiek/edit#' " +
                                            "target='blank'>Click here for detailed documentation.</a>"))
    location_history = forms.JSONField(
                        widget=LocationHistoryWidget(attrs={"rows": 10, "cols": 120}),
                        required=False,
                        disabled=True)

    def get_annotated_url(self):
        return Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__url")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__url")),
            default=None,
        )

    def get_resource_id(self):
        return Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__id")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__id")),
            default=None,
        )

    def get_resource_type(self):
        return Case(
            When(supplementalcontent__isnull=False, then=Value("supplementalcontent")),
            When(federalregisterdocument__isnull=False, then=Value("federalregisterdocument")),
            default=None,
        )

    def get_resource_name(self):
        return Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__name")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__name")),
            default=None,
        )

    def check_duplicates(self):
        query = AbstractResource.objects.all().annotate(url=self.get_annotated_url(),
                                                        res_id=self.get_resource_id(),
                                                        type=self.get_resource_type(),
                                                        name=self.get_resource_name(),
                                                        ).filter(url=self.cleaned_data.get('url'))

        resources = []
        if query.count() == 0:
            return False
        elif query.count() == 1:
            if self.instance.id and query.filter(id=self.instance.id).count() == 1:
                return False
        for res in query:
            resources.append({'type': res.type, 'id': str(res.res_id), "name": res.name})
        return resources

    def resource_links(self, resources):
        display_text = "The url is also used on the following resources:<br>"
        display_text = display_text + "".join(
                                 "<a href={}>{}</a><br>".format(
                                  reverse('admin:{}_{}_change'.format("resources", res['type']),
                                          args=(res['id'],)), res['type'] + " " + str(res['name']))
                                 for res in resources)
        if display_text:
            return mark_safe(display_text)  # noqa: S308
        return "-"

    def clean(self):
        cleaned_data = super().clean()
        dup_resources = self.check_duplicates()
        if dup_resources:
            urls = self.resource_links(dup_resources)
            self.add_error('url', urls)
        return cleaned_data


class SupContentForm(ResourceForm):
    class Meta:
        model = SupplementalContent
        fields = "__all__"

    def save(self, commit=True):
        return super(SupContentForm, self).save(commit=commit)


class FederalResourceForm(ResourceForm):
    doc_types = [('RFI', 'RFI'), ('NPRM', 'NPRM'), ("Final", 'Final')]

    class Meta:
        model = FederalRegisterDocument
        fields = "__all__"

    # We want to make sure that if there was a different value from doc type before that we preserve it.
    def __init__(self, *args, **kwargs):
        super(FederalResourceForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            CHOICES_INCLUDING_DB_VALUE = [(self.instance.doc_type,) * 2] + self.doc_types
            self.fields['doc_type'] = forms.ChoiceField(
                choices=CHOICES_INCLUDING_DB_VALUE)

    def save(self, commit=True):
        return super(FederalResourceForm, self).save(commit=commit)


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv"}))


@admin.register(SupplementalContent)
class SupplementalContentAdmin(AbstractResourceAdmin):
    change_list_template = "admin/import_resources_button.html"
    form = SupContentForm
    list_display = ("date", "name", "description", "category", "updated_at", "approved", "name_sort")
    list_display_links = ("date", "name", "description", "category", "updated_at")
    search_fields = ["date", "name", "description"]

    fieldsets = [
        (
            None,
            {
                "fields": ["approved", "name", "description", "date", "url", "category", "subjects", "locations"],
            },
        ),
        (
            "Statute Reference Locations",
            {
                "classes": ["collapse"],
                "fields": ["statute_locations"],
            },
        ),
        (
            "U.S.C. Reference Locations",
            {
                "classes": ["collapse"],
                "fields": ["usc_locations"],
            },
        ),
        (
            "Add Bulk Locations",
            {
                "classes": ["collapse"],
                "fields": ["bulk_title", "bulk_locations"],
            },
        ),
        (
            None,
            {
                "fields": ["internal_notes", "location_history"],
            },
        ),
    ]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import_resources/', self.show_import_resources_page),
        ]
        return my_urls + urls

    # Checks to see that there are atleast name and url
    def check_required_fields(self, row):
        return len(row) >= 3 and row[0]

    def resource_link(self, obj):
        display_text = "<a href={} target='blank'>{}</a>".format(
                                  reverse('admin:{}_{}_change'.format("resources", "supplementalcontent"),
                                          args=(obj.id,)), obj.name)
        if display_text:
            return mark_safe(display_text)  # noqa: S308
        return "-"

    def add_content(self, reader):
        categories = AbstractCategory.objects.all()
        added_resources = []
        failed_resources = []

        next(reader)
        for row in reader:
            if self.check_required_fields(row):
                try:
                    bulk_adds, bad_locations = self.get_bulk_locations(row[4])
                    try:
                        category = categories.get(name__iexact=row[3])
                    except AbstractCategory.DoesNotExist:
                        category = None
                    content, created = SupplementalContent.objects.get_or_create(
                        name=row[0],
                        description=row[1],
                        url=row[2],
                        approved=False,
                        category=category,
                    )
                except Exception:
                    created = False
            else:
                created = False
            if created:
                link = self.resource_link(content)
                resource = {"name": link, "category": "", "added_locations": bulk_adds, "failed_locations": bad_locations}
                if bulk_adds:
                    for location in bulk_adds:
                        content.locations.add(location.abstractlocation_ptr)
                    content.save()

                resource["category"] = category if category else f"Invalid category: { row[3] }"
                added_resources.append(resource)
            elif not created:
                failed_resources.append({"row": row, "line_number": reader.line_num})
        return added_resources, failed_resources

    def resource_reader(self, csv_file):
        return csv.reader(csv_file.read().decode('utf8').splitlines(),
                          quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)

    def show_import_resources_page(self, request):
        if "get_template" in request.GET:
            columns = ["name", "description", "url", "category", "locations"]
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": 'attachment; filename="content_upload.csv"'},
            )
            writer = csv.writer(response)
            writer.writerow(columns)
            return response
        if request.method == "POST":
            successes, failures = [], []
            error = None
            try:
                csv_file = request.FILES["csv_file"].file
                reader = self.resource_reader(csv_file)
                successes, failures = self.add_content(reader)
            except Exception:
                error = "Something went wrong.  Please check that the file you are trying to upload is a csv and not corrupted."

            return render(request, "admin/resources_imported.html", context={
                "added_resources": successes,
                "failures": failures,
                "error": error
            })
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/import_resources.html", payload)


@admin.register(FederalRegisterDocument)
class FederalRegisterDocumentAdmin(AbstractResourceAdmin):
    form = FederalResourceForm
    list_display = ("date", "name", "description", "in_group", "docket_numbers",
                    "document_number", "category", "doc_type", "updated_at", "approved")
    list_display_links = ("date", "name", "description", "in_group", "docket_numbers",
                          "document_number", "category", "doc_type", "updated_at")
    search_fields = ["date", "name", "description", "docket_numbers", "document_number"]

    fieldsets = [
        (
            None,
            {
                "fields": ["approved", "docket_numbers", "group", "document_number", "name", "correction", "withdrawal",
                           "description", "date", "url", "category", "subjects", "doc_type", "locations"],
            },
        ),
        (
            "Statute Reference Locations",
            {
                "classes": ["collapse"],
                "fields": ["statute_locations"],
            },
        ),
        (
            "U.S.C. Reference Locations",
            {
                "classes": ["collapse"],
                "fields": ["usc_locations"],
            },
        ),
        (
            "Add Bulk Locations",
            {
                "classes": ["collapse"],
                "fields": ["bulk_title", "bulk_locations"],
            },
        ),
        (
            None,
            {
                "fields": ["internal_notes", "location_history"],
            },
        ),
    ]

    def in_group(self, obj):
        group = str(obj.group)
        return group[0:20] + "..." if len(group) > 20 else group

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch("group", FederalRegisterDocumentGroup.objects.all()),
        )


class FederalRegisterDocumentGroupForm(forms.ModelForm):
    documents = forms.ModelMultipleChoiceField(
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
            self.fields["documents"].initial = self.instance.documents.all()

    def save(self, commit=True):
        group = super().save(commit=False)
        group.save()
        group.documents.set(self.cleaned_data["documents"])
        group.save()
        return group

    class Meta:
        model = FederalRegisterDocumentGroup
        fields = ("docket_number_prefixes", "documents")


@admin.register(FederalRegisterDocumentGroup)
class FederalRegisterDocumentGroupAdmin(BaseAdmin):
    form = FederalRegisterDocumentGroupForm
    admin_priority = 250
    list_display = ("docket_number_prefixes", "number_of_documents")
    list_display_links = ("docket_number_prefixes", "number_of_documents")
    search_fields = ["docket_number_prefixes"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(number_of_documents=Count("documents"))

    def number_of_documents(self, obj):
        return obj.number_of_documents


# Custom app list function, allows ordering Django Admin models by "admin_priority", low to high
def get_app_list(self, request):
    app_dict = self._build_app_dict(request)
    for app_name in app_dict.keys():
        app = app_dict[app_name]
        model_priority = {
            model['object_name']: getattr(
                site._registry[apps.get_model(app_name, model['object_name'])],
                'admin_priority',
                20
            )
            for model in app['models']
        }
        app['models'].sort(key=lambda x: model_priority[x['object_name']])
        yield app


# Patch Django's built in get_app_list function
admin.AdminSite.get_app_list = get_app_list
