import re

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse

import requests
from solo.admin import SingletonModelAdmin

from .models import SiteConfiguration, StatuteLinkConverter

from xml.dom import minidom


MARKUP_PATTERN = r"</?[^>]+>"
DASH_PATTERN = r"[—–-–-]"
SECTION_PATTERN = rf"sec.?\s*(\d+[a-z0-9]*(?:{DASH_PATTERN}+[a-z0-9]+)?).?"
CONVERSION_PATTERN = rf"{SECTION_PATTERN}\s*\[\s*(\d+)\s*u.?s.?c.?\s*(\d+[a-z0-9]*(?:{DASH_PATTERN}+[a-z0-9]+)?)\s*\]"
TITLE_PATTERN = rf"title\s+([a-z]+)\s*{DASH_PATTERN}*(?:\s+of\s+the\s+[a-z0-9\s]*?(?=\bact\b))?"
SECTION_APPEND_PATTERN = rf"({DASH_PATTERN}+[a-z0-9]+)."

MARKUP_REGEX = re.compile(MARKUP_PATTERN)
DASH_REGEX = re.compile(DASH_PATTERN)
SECTION_REGEX = re.compile(SECTION_PATTERN, re.IGNORECASE)
CONVERSION_REGEX = re.compile(CONVERSION_PATTERN, re.IGNORECASE)
TITLE_REGEX = re.compile(TITLE_PATTERN, re.IGNORECASE)
SECTION_APPEND_REGEX = re.compile(SECTION_APPEND_PATTERN, re.IGNORECASE)


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin):
    pass


@admin.register(StatuteLinkConverter)
class StatuteLinkConverterAdmin(admin.ModelAdmin):
    change_list_template = "admin/import_conversions_button.html"
    list_per_page = 200
    search_fields = ["act", "section", "title", "usc", "source_url"]
    ordering = ("act", "section", "title", "usc", "source_url")
    readonly_fields = ("source_url",)

    fieldsets = (
        (None, {
            "fields": (
                "statute_title",
                "act",
                "section",
                "name",
                "title",
                "usc",
                "source_url",
            ),
            "description": 'For a detailed guide on Statute Link Conversions, please <a target="_blank" '
                           'href="https://docs.google.com/document/d/14se_BSANJ2Q7Y8OjOLpMLSAye5MpIEkOBhA9-_1RpJY/edit#">'
                           'click here</a>.',
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import_conversions/', self.show_import_conversions_page),
        ]
        return my_urls + urls

    def import_conversions(self, text, url, act):
        conversions = []
        failures = []
        toc = self.parse_toc(text)
        text = MARKUP_REGEX.sub("", text)  # Strips HTML/XML tags from the response text
        text = DASH_REGEX.sub("-", text)  # Replace em dash and en dash with regular dash
        matches = CONVERSION_REGEX.findall(text)

        for section, title, usc in matches:
            data = {
                "section": section,
                "title": title,
                "usc": usc,
                "act": act,
                "source_url": url,
            }
            if section in toc:
                data["name"] = toc[section]["name"]
                data["statute_title"] = toc[section]["statute_title"]
            instance, created = self.model.objects.get_or_create(**data)
            if created:
                data["id"] = instance.id
                if section in toc:
                    conversions.append(data)
                else:
                    failures.append(data)

        return conversions, len(matches), failures

    def parse_toc(self, text):
        try:
            dom = minidom.parseString(text)
        except Exception as e:
            raise ValidationError(f"invalid XML detected: {str(e)}")

        # search for a title
        title = None
        for i in dom.getElementsByTagName("containsShortTitle"):
            match = TITLE_REGEX.search(i.firstChild.nodeValue)
            if match:
                title = match.group(1).upper().strip()
                break

        # parse table of contents
        toc = {}
        for i in dom.getElementsByTagName("referenceItem"):
            role = i.getAttribute("role")
            if role == "title":
                designator = i.getElementsByTagName("designator")
                if not designator:
                    raise ValidationError("invalid XML detected: 'referenceItem' does not have a 'designator'.")
                match = TITLE_REGEX.search(designator[0].firstChild.nodeValue)
                if not match:
                    raise ValidationError("invalid XML detected: 'referenceItem' contains an invalid Title.")
                title = match.group(1)
            elif role == "section":
                designator = i.getElementsByTagName("designator")
                if not designator:
                    continue
                section = SECTION_REGEX.search(designator[0].firstChild.nodeValue)
                label = i.getElementsByTagName("label")
                if label and section and title:
                    section = section.group(1)
                    label = label[0].firstChild.nodeValue.strip()
                    section_append = SECTION_APPEND_REGEX.match(label)
                    if section_append:
                        section += DASH_REGEX.sub("-", section_append.group(1).strip())
                        label = SECTION_APPEND_REGEX.sub("", label).strip()
                    toc[section] = {
                        "name": label,
                        "statute_title": title,
                    }
        return toc

    def try_import(self, url, act):
        if not url:
            raise ValidationError("you must enter a URL.")
        if not act:
            raise ValidationError("you must enter an Act, for example \"Social Security Act\".")

        try:
            URLValidator(schemes=["http", "https"])(url)
        except ValidationError:
            raise ValidationError(f"{url} is not a valid URL." if url else "you must enter a URL.")

        response = requests.get(url)
        response.raise_for_status()
        conversions, matches, failures = self.import_conversions(response.text, url, act)
        if conversions or failures:
            return conversions, failures
        if matches:
            raise ValidationError(f"all conversions contained in {url} already exist.")
        else:
            raise ValidationError(f"{url} did not contain any valid conversions.")

    def show_import_conversions_page(self, request):
        error = None

        if "import" in request.POST:
            url = request.POST.get("url", "").strip()
            act = request.POST.get("act", "").strip()
            try:
                conversions, failures = self.try_import(url, act)
                return render(request, "admin/conversions_imported.html", context={
                    "num_conversions": len(conversions) + len(failures),
                    "conversions": conversions,
                    "failures": failures,
                })
            except ValidationError as e:
                error = e.message
            except Exception as e:
                error = str(e)

        if "return" in request.POST or error:
            num_conversions = request.POST.get("num_conversions", 0)
            app = self.model._meta.app_label
            model = self.model._meta.model_name
            message = f"Failed to import: {error}" if error else f"Successfully imported {num_conversions} conversions."
            self.message_user(request, message, messages.ERROR if error else messages.SUCCESS)
            return HttpResponseRedirect(reverse(f"admin:{app}_{model}_changelist"))

        return render(request, "admin/import_conversions.html", context={})
