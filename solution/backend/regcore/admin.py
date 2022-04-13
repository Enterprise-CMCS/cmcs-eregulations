from django.contrib import admin
from django.db import models
from django.forms import TextInput

from solo.admin import SingletonModelAdmin

from supplemental_content.admin import BaseAdmin
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
                'attempts',
                'loglevel',
                'upload_supplemental_locations',
                'log_parse_errors',
                'skip_versions',
            ),
            'description': "<b>Please note:</b> Changes to the parser configuration "
                           "will not take effect until the next scheduled parser run!",
        }),
    )


@admin.register(Synonym)
class SectionAdmin(BaseAdmin):
    admin_priority = 20
    ordering = ('baseWord',)

    class Media:
        css = {
            "all": ("css/admin/synonym.css",)
        }
