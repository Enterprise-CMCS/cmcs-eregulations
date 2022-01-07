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
