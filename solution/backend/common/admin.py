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

from django.http import HttpResponse
from django.core import serializers


class ExportJSONMixin:
    def export_all_as_json(self, request):

        format = "json"
        indent = 2

        model = self.model
        pk_list = model.objects.values_list('pk', flat=True)
        queryset = model.objects.all()
        objects = list(queryset)
        parents = []
        if len(objects[0].__class__.__bases__):
            base = objects[0].__class__.__bases__[0]
            # Model is the top level class that everything derives from
            while base.__name__ != 'Model':
                print(base.__class__.__name__)
                r = list(base.objects.filter(pk__in=pk_list))
                base = r[0].__class__.__bases__[0]
                parents = r + parents

        parents.extend(objects)
        stream = serializers.serialize(format, parents, indent=indent)
        response = HttpResponse(stream, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.json'.format(model._meta)
        return response


class NewBaseAdmin(admin.ModelAdmin, ExportJSONMixin):
    change_list_template = "admin/export_all_json.html"
    list_per_page = 200
    admin_priority = 20
    actions = ["export_as_json"]

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

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('export_all_json/', self.export_all_as_json),
        ]
        return my_urls + urls


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
