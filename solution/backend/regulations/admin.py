import re

import requests
from defusedxml.minidom import parseString
from django.contrib import admin, messages
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from solo.admin import SingletonModelAdmin

from .models import (
    RegulationLinkConfiguration,
    SiteConfiguration,
    StatuteLinkConfiguration,
    StatuteLinkConverter,
)

# Finds all HTML/XML tags for removal, e.g. "<a href="#">abc</a>" becomes "abc".
MARKUP_PATTERN = r"</?[^>]+>"

# Finds all possible representations of dashes for replacement with the standard ASCII dash "-".
DASH_PATTERN = r"[—–-–-]"

# Finds section identifiers, e.g. "Sec. 1192", "Sec. 1192A-2g", etc.
SECTION_PATTERN = rf"sec.?\s*(\d+[a-z0-9]*(?:{DASH_PATTERN}+[a-z0-9]+)?).?"

# Finds section conversion patterns, e.g. "Sec. 1902 [42 U.S.C. 123B-2C]" and similar.
CONVERSION_PATTERN = rf"{SECTION_PATTERN}\s*\[\s*(\d+)\s*u.?s.?c.?\s*(\d+[a-z0-9]*(?:{DASH_PATTERN}+[a-z0-9]+)?)\s*\]"

# Finds title identifiers, e.g. "Title IX of the Social Security Act", "Title IX", "Title IX of the Act", etc.
TITLE_PATTERN = rf"title\s+([a-z]+)\s*{DASH_PATTERN}*(?:\s+of\s+the\s+[a-z0-9\s]*?(?=\bact\b))?"

# Finds section parts that are after a dash, e.g. "1902-1G" will match "1G".
# Used when the "-1G" part is contained within another XML tag.
# For example "<X>Sec 1902</X><Y>-1G. Name of this section</Y>".
# This occurs frequently in the XML table of contents and so must be accounted for.
SECTION_APPEND_PATTERN = rf"({DASH_PATTERN}+[a-z0-9]+)."

MARKUP_REGEX = re.compile(MARKUP_PATTERN)
DASH_REGEX = re.compile(DASH_PATTERN)
SECTION_REGEX = re.compile(SECTION_PATTERN, re.IGNORECASE)
CONVERSION_REGEX = re.compile(CONVERSION_PATTERN, re.IGNORECASE)
TITLE_REGEX = re.compile(TITLE_PATTERN, re.IGNORECASE)
SECTION_APPEND_REGEX = re.compile(SECTION_APPEND_PATTERN, re.IGNORECASE)

roman_table = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}


# Convert roman numerals to integers. Returns 0 if invalid.
def roman_to_int(roman):
    result = 0
    for i in range(len(roman) - 1, -1, -1):
        if roman[i] not in roman_table:
            return 0
        num = roman_table[roman[i]]
        result = result - num if 3 * num < result else result + num
    return result


class OidcAdminAuthenticationBackend(OIDCAuthenticationBackend):
    def verify_claims(self, claims) -> bool:
        return (
                super().verify_claims(claims)
                and claims.get("email_verified", False)
        )

    def create_user(self, claims) -> User:
        email = claims.get("email")
        jobcodes = claims.get("jobcodes")

        if jobcodes:
            with transaction.atomic():
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    user = User.objects.create_user(email, email)

                user = self.update_user(user, claims)
                user.save()

                return user
        else:
            return None


    @transaction.atomic
    def update_user(self, user: User, claims) -> User:
        """Update existing user with new claims, if necessary save, and return user"""
        # Determine group membership based on jobcodes and add the user to the groups

        jobcodes = claims.get("jobcodes")
        jobcodes_list = jobcodes.split(",")  # Split the jobcodes string into a list

        # Extract relevant jobcode information
        relevant_jobcodes = [jobcode.replace("cn=", "") for jobcode in jobcodes_list if jobcode.startswith("cn=EREGS_")]
        group_mapping = {
            "EREGS_ADMIN": "e-Regs-Admin",
            "EREGS_MANAGER": "e-Regs-Manager",
            "EREGS_EDITOR": "e-Regs-Editor",
            "EREGS_READER": "e-Regs-Reader",
        }

        groups_to_add = [group_mapping.get(jobcode) for jobcode in relevant_jobcodes if jobcode in group_mapping]

        # Add the user to the determined groups
        user.groups.set(Group.objects.filter(name__in=groups_to_add))

        first_name = claims.get("firstName")
        if first_name:
            user.first_name = first_name

        last_name = claims.get("lastName")
        if last_name:
            user.last_name = last_name

        # Check if there are any jobcodes
        if relevant_jobcodes:
            user.is_active = True
        else:
            user.is_active = False
        user.save()

        return user


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin):
    fieldsets = (
        (None, {
            "fields": (
                'allow_indexing',
                ('us_code_house_gov_date_type', 'us_code_house_gov_date'),
                ('ssa_gov_compilation_date_type', 'ssa_gov_compilation_date'),
                ('statute_compilation_date_type', 'statute_compilation_date'),
                ('us_code_annual_date_type', 'us_code_annual_date'),
            ),
            "description": 'Configure crawling for the whole site and dates for statute sources.'
        }),
    )


@admin.register(StatuteLinkConfiguration)
class StatuteLinkConfigurationAdmin(SingletonModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": ["link_statute_refs", "link_usc_refs"],
            },
        ),
        (
            "Statute Ref Link Exceptions",
            {
                "classes": ["collapse"],
                "fields": ["statute_ref_exceptions"],
            },
        ),
        (
            "U.S.C. Ref Link Exceptions",
            {
                "classes": ["collapse"],
                "fields": ["usc_ref_exceptions"],
            },
        ),
    ]


@admin.register(RegulationLinkConfiguration)
class RegulationLinkConfigurationAdmin(SingletonModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": ["link_to_ecfr", "link_cfr_refs"],
            },
        ),
        (
            "CFR Ref Link Exceptions",
            {
                "classes": ["collapse"],
                "fields": ["cfr_ref_exceptions"],
            },
        ),
    ]


@admin.register(StatuteLinkConverter)
class StatuteLinkConverterAdmin(admin.ModelAdmin):
    change_list_template = "admin/import_conversions_button.html"
    list_per_page = 200
    search_fields = ["act", "section", "title", "usc", "source_url"]
    ordering = ("act", "section", "title", "usc", "source_url")
    readonly_fields = ("source_url", "statute_title_roman")

    fieldsets = (
        (None, {
            "fields": (
                "statute_title",
                "statute_title_roman",
                "act",
                "section",
                "name",
                "title",
                "usc",
                "source_url",
            ),
            "description": 'For a detailed guide on Statute Link Conversions, please <a target="_blank" '
                           'rel="noopener noreferrer" '
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
                title = toc[section]["statute_title"]
                try:
                    title = int(title)
                except ValueError:
                    title = roman_to_int(title)
                if title:
                    data["statute_title"] = title
            instance, created = self.model.objects.get_or_create(**data)
            if created:
                data["id"] = instance.id
                if section in toc and "statute_title" in data:
                    conversions.append(data)
                else:
                    failures.append(data)

        return conversions, len(matches), failures

    def parse_toc(self, text):
        try:
            dom = parseString(text)
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
                title = match.group(1).upper().strip()
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
                        label = SECTION_APPEND_REGEX.sub("", label, 1).strip()
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

        response = requests.get(url, timeout=10)
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
