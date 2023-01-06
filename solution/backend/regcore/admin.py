from django.contrib import admin
from django.db import models
from django.forms import TextInput

from solo.admin import SingletonModelAdmin

from resources.admin import BaseAdmin
from .models import ParserConfiguration, TitleConfiguration
from .search.models import Synonym, SearchConfiguration
from django.contrib.admin.models import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    # to have a date-based drilldown navigation in the admin page
    date_hierarchy = 'action_time'

    # to filter the resultes by users, content types and action flags
    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    # when searching the user will be able to search in both object_repr and change_message
    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'action_flag',
    ]


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


@admin.register(Synonym)
class SynonymAdmin(BaseAdmin):
    change_list_template = "admin/synonyms.html"
    admin_priority = 20
    ordering = ('baseWord',)


@admin.register(SearchConfiguration)
class SearchAdmin(BaseAdmin):
    admin_priority = 78
    list_display = ("config", "value")
    fields = ("config", "value")
