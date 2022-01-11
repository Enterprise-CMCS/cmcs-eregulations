from django.contrib import admin
from django.db import models
from django.forms import TextInput

from solo.admin import SingletonModelAdmin

from .models import ParserConfiguration, TitleConfiguration


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
            'description': "<b>Please note:</b> Changes to the parser configuration will not take effect until the next scheduled parser run!",
        }),
    )