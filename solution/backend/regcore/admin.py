from django.contrib import admin
from django.db import models
from django.forms import TextInput

from solo.admin import SingletonModelAdmin

from resources.admin import BaseAdmin
from .models import ParserConfiguration, TitleConfiguration
from .search.models import Synonym


class TitleConfigurationInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput(attrs={
                'style': 'width: calc(100% - 1em);',
            })
        }
    }
    model = TitleConfiguration
    extra = 1


@admin.register(ParserConfiguration)
class ParserConfigurationAdmin(SingletonModelAdmin):
    inlines = (TitleConfigurationInline,)
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

    # TODO: Remove this method when FR parser work is complete (EREGCSC-1390)
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["skip_fr_documents"].disabled = True
        return form


@admin.register(Synonym)
class SynonymAdmin(BaseAdmin):
    change_list_template = "admin/synonyms.html"
    admin_priority = 20
    ordering = ('baseWord',)
