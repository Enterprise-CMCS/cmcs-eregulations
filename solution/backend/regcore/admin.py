
from django.contrib import admin
from django.db import models
from django.forms import TextInput
from solo.admin import SingletonModelAdmin

from .models import ParserConfiguration, PartConfiguration


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
