import re

from django.contrib import admin, messages
from django.shortcuts import render
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

import requests

from solo.admin import SingletonModelAdmin

from .models import SiteConfiguration, SSAToUSCConverter


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin):
    pass

@admin.register(SSAToUSCConverter)
class SSAToUSCConverterAdmin(admin.ModelAdmin):
    change_list_template = "admin/import_conversions_button.html"
    list_per_page = 200
    search_fields = ["section", "title", "usc"]
    ordering = ("title", "section", "usc")
    fields = ("section", "title", "usc")

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import_conversions/', self.show_import_conversions),
        ]
        return my_urls + urls

    def import_conversions(self, text):
        conversions = []
        text = re.sub("</?[^>]+>", "", text)  # Strips XML tags from the response text
        matches = re.findall("[Ss][Ee][Cc].?\\s*(\\d+).?\\s*\[(\\d+)\\s*[Uu].?[Ss].?[Cc].?\\s*(\\w+)\]", text)  # Find all conversions
        for section, title, usc in matches:
            instance, created = self.model.objects.get_or_create(section=section, title=title, usc=usc)
            if created:
                conversions.append({
                    "section": instance.section,
                    "title": instance.title,
                    "usc": instance.usc
                })
        return conversions, len(matches)
    
    def show_import_conversions(self, request):
        error = None

        if "import" in request.POST:
            url = request.POST.get("url", "").strip()
            try:
                URLValidator(schemes=["http", "https"])(url)
                response = requests.get(url)
                response.raise_for_status()
                conversions, matches = self.import_conversions(response.text)
                if conversions:
                    return render(request, "admin/conversions_imported.html", context={
                        "num_conversions": len(conversions),
                        "conversions": conversions,
                    })
                if matches and not conversions:
                    error = f"all conversions contained in {url} already exist!"
                else:
                    error = f"{url} did not contain any valid conversions!"
            except ValidationError:
                error = f"{url} is not a valid URL!" if url else "you must enter a URL!"
            except requests.exceptions.RequestException as e:
                error = str(e)

        if "return" in request.POST or error:
            num_conversions = request.POST.get("num_conversions", 0)
            app = self.model._meta.app_label
            model = self.model._meta.model_name
            message = f"Failed to import: {error}" if error else f"Successfully imported {num_conversions} conversions!"
            self.message_user(request, message, messages.ERROR if error else messages.SUCCESS)
            return HttpResponseRedirect(reverse(f"admin:{app}_{model}_changelist"))

        return render(request, "admin/import_conversions.html", context={})
