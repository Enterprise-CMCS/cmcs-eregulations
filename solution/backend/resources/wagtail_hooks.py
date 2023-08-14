from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import InternalDocument
from django.urls import path, reverse

from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from wagtail import hooks


class InternalAdmin(ModelAdmin):
    model = InternalDocument
    menu_label = "Internal Documents"
    menu_icon = "pick"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display =("name", "description")
    search_fields = ("name"),

modeladmin_register(InternalAdmin)
