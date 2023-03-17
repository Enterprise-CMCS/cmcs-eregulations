import datetime
from model_utils.managers import InheritanceManager, InheritanceQuerySet
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db import models
from django_jsonform.models.fields import ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from solo.models import SingletonModel
import re


class ProxyManager(models.Manager):
    def __init__(self, type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = type

    def get_queryset(self):
        return super().get_queryset().filter(type=self.type)
    
    def create(self, *args, **kwargs):
        return super().create(type=self.type, *args, **kwargs)


class DisplayNameFieldMixin:
    @property
    def display_name(self):
        return str(self)


# Location models


class Location(models.Model, DisplayNameFieldMixin):
    SECTION = 0
    SUBPART = 1
    LOCATION_TYPES = [
        (SECTION, "Section"),
        (SUBPART, "Subpart"),
    ]

    type = models.IntegerField(choices=LOCATION_TYPES, default=SECTION)
    title = models.IntegerField()
    part = models.IntegerField()
    subpart = models.CharField(max_length=12, null=True, blank=True)
    section = models.IntegerField(null=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")

    def __str__(self):
        return [
            f"{self.title} CFR {self.part}.{self.section}",
            f"{self.title} CFR {self.part} Subpart {self.subpart}",
        ][self.type]

    class Meta:
        unique_together = [
            ["type", "title", "part", "section"],
            ["type", "title", "part", "subpart"],
        ]


class Section(Location):
    TYPE = Location.SECTION
    objects = ProxyManager(TYPE)

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        proxy = True


class Subpart(Location):
    TYPE = Location.SUBPART
    objects = ProxyManager(TYPE)

    class Meta:
        verbose_name = "Subpart"
        verbose_name_plural = "Subparts"
        proxy = True


# Category models


class CategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            is_fr_doc_category=models.ExpressionWrapper(
                ~models.Q(fr_doc_category_config=None),
                output_field=models.BooleanField()
            )
        )


class BaseCategory(models.Model, DisplayNameFieldMixin):
    CATEGORY = 0
    SUB_CATEGORY = 1
    CATEGORY_TYPES = [
        (CATEGORY, "Category"),
        (SUB_CATEGORY, "Sub-category")
    ]

    type = models.IntegerField(choices=CATEGORY_TYPES, default=CATEGORY)
    name = models.CharField(max_length=512)
    description = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=0, blank=True)
    show_if_empty = models.BooleanField(default=False)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    objects = CategoryManager()

    def __str__(self):
        return f"{self.name} ({self.CATEGORY_TYPES[self.type][1]})"

    class Meta:
        unique_together = [
            ["type", "name", "description", "order"],
            ["type", "name", "description", "order", "parent"],
        ]


class CategoryProxyManager(ProxyManager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            is_fr_doc_category=models.ExpressionWrapper(
                ~models.Q(fr_doc_category_config=None),
                output_field=models.BooleanField()
            )
        )


class Category(BaseCategory):
    TYPE = BaseCategory.CATEGORY
    objects = CategoryProxyManager(TYPE)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        proxy = True


class SubCategory(BaseCategory):
    TYPE = BaseCategory.SUB_CATEGORY
    objects = CategoryProxyManager(TYPE)

    class Meta:
        verbose_name = "Sub-category"
        verbose_name_plural = "Sub-categories"
        proxy = True


# Resource models


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


class ResourceGroup(models.Model, DisplayNameFieldMixin):
    FEDERAL_REGISTER_DOCUMENT_GROUP = 0
    RESOURCEGROUP_TYPES = [
        (FEDERAL_REGISTER_DOCUMENT_GROUP, "Federal Register Document Group"),
    ]

    type = models.IntegerField(choices=RESOURCEGROUP_TYPES, default=FEDERAL_REGISTER_DOCUMENT_GROUP)

    # Federal Register Documents
    docket_number_prefixes = ArrayField(
        models.CharField(max_length=255, blank=True, null=True),
        default=list,
        blank=True,
        help_text="Common prefixes to use when grouping Federal Register Documents, "
                  "e.g. \"CMS-1234-\" to match any docket number starting with that string.",
    )

    def __str__(self):
        return [
            f"\"{', '.join(self.docket_number_prefixes)}\" group"
        ][self.type]

    class Meta:
        unique_together = ["type", "docket_number_prefixes"]


class FederalRegisterDocumentGroup(ResourceGroup):
    TYPE = ResourceGroup.FEDERAL_REGISTER_DOCUMENT_GROUP
    objects = ProxyManager(TYPE)

    class Meta:
        verbose_name = "Federal Register Doc Group"
        verbose_name_plural = "Federal Register Doc Groups"
        proxy = True


class Resource(models.Model, DisplayNameFieldMixin):
    SUPPLEMENTAL_CONTENT = 0
    FEDERAL_REGISTER_DOCUMENT = 1
    RESOURCE_TYPES = [
        (SUPPLEMENTAL_CONTENT, "Supplemental Content"),
        (FEDERAL_REGISTER_DOCUMENT, "Federal Register Document"),
    ]

    # Common fields
    type = models.IntegerField(choices=RESOURCE_TYPES, default=SUPPLEMENTAL_CONTENT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=True)
    category = models.ForeignKey(BaseCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="resources")
    locations = models.ManyToManyField(Location, blank=True, related_name="resources")
    related_resources = models.ManyToManyField("self", blank=True, symmetrical=False)
    group = models.ForeignKey(ResourceGroup, null=True, blank=True, on_delete=models.SET_NULL, related_name="resources")
    location_history = models.JSONField(default=list)

    # Supplemental Content and Federal Register Document fields
    name = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(max_length=512, null=True, blank=True)
    internal_notes = models.TextField(null=True, blank=True)
    date = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Leave blank or enter one of: \"YYYY\", \"YYYY-MM\", or \"YYYY-MM-DD\".",
        validators=[RegexValidator(
            regex="^\\d{4}((-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]))|(-(0[1-9]|1[0-2])))?$",
            message="Date field must be blank or of format \"YYYY\", \"YYYY-MM\", or \"YYYY-MM-DD\"! "
                    "For example: 2021, 2021-01, or 2021-01-31.",
        )],
    )

    # Federal Register Document fields
    docket_numbers = ArrayField(models.CharField(max_length=255, blank=True, null=True), default=list, blank=True)
    document_number = models.CharField(max_length=255, blank=True, null=True)
    correction = models.BooleanField(default=False)
    withdrawal = models.BooleanField(default=False)
    doc_type = models.CharField(blank=True, max_length=255)

    # Sort fields
    name_sort = NaturalSortField("name", null=True)
    description_sort = NaturalSortField("description", null=True)

    def __str__(self):
        return [
            f"{self.date} {self.name} {self.description[:50]}",
            f"{self.date} {self.document_number}: {self.name}",
        ][self.type]

    def clean(self):
        # If a day is entered into the date field, validate for months with less than 31 days.
        if self.date is not None:
            date_fields = self.date.split("-")
            if len(date_fields) == 3:
                (year, month, day) = date_fields
                try:
                    _ = datetime.date(int(year), int(month), int(day))
                except ValueError:
                    raise ValidationError(f'{day} is not a valid day for the month of {month}!')


class SupplementalContent(Resource):
    TYPE = Resource.SUPPLEMENTAL_CONTENT
    objects = ProxyManager(TYPE)

    class Meta:
        verbose_name = "Supplemental Content"
        verbose_name_plural = "Supplemental Content"
        proxy = True


class FederalRegisterDocument(Resource):
    TYPE = Resource.FEDERAL_REGISTER_DOCUMENT
    objects = ProxyManager(TYPE)

    class Meta:
        verbose_name = "Federal Register Document"
        verbose_name_plural = "Federal Register Documents"
        proxy = True


def update_related_resources(group_id):
    post_save.disconnect(post_save_resource, sender=Resource)
    post_save.disconnect(post_save_resource_group, sender=ResourceGroup)
    for resource in Resource.objects.filter(group=group_id):
        resource.related_resources.set(resource.group.resources.exclude(id=resource.id).order_by("-date"))
        resource.save()
    post_save.connect(post_save_resource, sender=Resource)
    post_save.connect(post_save_resource_group, sender=ResourceGroup)


@receiver(post_save, sender=ResourceGroup)
def post_save_resource_group(sender, instance, **kwargs):
    update_related_resources(instance.id)


@receiver(post_save, sender=Resource)
def post_save_resource(sender, instance, **kwargs):
    if instance.group:
        update_related_resources(instance.group)


# Singleton model for configuring resources app


class ResourcesConfiguration(SingletonModel):
    fr_doc_category = models.ForeignKey(
        BaseCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="fr_doc_category_config",
        help_text="The category that contains Federal Register Documents. This affects "
                  "all newly uploaded Federal Register Documents.",
    )

    def __str__(self):
        return "Resources Configuration"

    class Meta:
        verbose_name = "Resources Configuration"
