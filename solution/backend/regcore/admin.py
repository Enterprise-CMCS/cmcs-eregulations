import csv

from django.contrib import admin, messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import models
from django.forms import TextInput
from django.shortcuts import redirect, render
from django.views import View
from solo.admin import SingletonModelAdmin

from common.admin import CustomAdminMixin

from .models import ParserConfiguration, PartConfiguration
from .search.models import Synonym


class BulkSynonymView(PermissionRequiredMixin, View):
    permission_required = 'search.add_synonym'

    def process_body(raw_synonyms):
        new_synonyms = []
        existing_synonyms = []
        reader = csv.reader(raw_synonyms, delimiter=',')
        for row in reader:
            related_words = []
            for syn in row:
                if syn:
                    new_syn, created = Synonym.objects.get_or_create(isActive=True, baseWord=syn.strip())
                    if created:
                        new_synonyms.append(syn)
                    else:
                        existing_synonyms.append(syn)
                    for word in related_words:
                        new_syn.synonyms.add(word)
                    related_words.append(new_syn)

        return new_synonyms, existing_synonyms

    def get(self, request):
        return render(request, 'add_synonym.html', {})

    def post(self, request):
        # csv package accepts this foo,"bar, baz" by default, but foo, "bar, baz" is not handled.  This allows for one
        # space to still work correctly.
        raw_synonyms = request.POST['raw_synonyms'].replace(', "', ',"').split("\r\n")
        new_synonyms, existing_synonyms = self.process_body(raw_synonyms)

        if new_synonyms:
            messages.add_message(
                request,
                messages.INFO,
                "The following synonyms have been added: " + ", ".join(new_synonyms)
            )
        if existing_synonyms:
            messages.add_message(
                request,
                messages.WARNING,
                "The following synonyms have not been added because they already exist: " +
                ", ".join(existing_synonyms)
            )
        return redirect("search/synonym/")


class PartConfigurationInline(admin.TabularInline):
    ordering = ("title", "value")
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput(attrs={
                'style': 'width: calc(100% - 1em);',
            })
        }
    }
    model = PartConfiguration
    extra = 0


@admin.register(ParserConfiguration)
class ParserConfigurationAdmin(SingletonModelAdmin):
    inlines = (PartConfigurationInline,)
    fieldsets = (
        (None, {
            'fields': (
                'workers',
                'loglevel',
                'upload_supplemental_locations',
                'log_parse_errors',
                'skip_reg_versions',
                'skip_fr_documents',
            ),
            'description': "<b>Please note:</b> Changes to the parser configuration "
                           "will not take effect until the next scheduled parser run!",
        }),
    )


@admin.register(Synonym)
class SynonymAdmin(CustomAdminMixin, admin.ModelAdmin):
    admin_priority = 20
    ordering = ('baseWord',)
