from typing import List

from django.http import JsonResponse
from django.views import View

from regulations.models import SectionContextBanner


class ContextBannersView(View):
    def get(self, request):
        try:
            title = int(request.GET.get("title"))
            part = int(request.GET.get("part"))
        except (TypeError, ValueError):
            return JsonResponse({"results": []})

        subpart = request.GET.get("subpart")
        section = request.GET.get("section")  # e.g., "75.104" or "104"

        qs = (
            SectionContextBanner.objects
            .filter(is_active=True, citation__title=title, citation__part=part)
            .select_related("citation")
        )

        # If a section is provided, narrow to that section only
        if section:
            # Normalize: allow "104" or "75.104"
            try:
                section_id = int(str(section).split(".")[-1])
            except ValueError:
                section_id = None
            if section_id is not None:
                qs = qs.filter(citation__section__section_id=section_id)
        elif subpart:
            # Otherwise, if a subpart is provided, show banners for that subpart
            qs = qs.filter(citation__section__parent__subpart_id=subpart)
        else:
            # No subpart or section specified → return empty list to avoid part-wide payloads
            return JsonResponse({"results": []})

        rows: List[dict] = list(qs.values(
            "citation__part",
            "citation__section__section_id",
            "citation__section__parent__subpart_id",
            "banner_html",
        ))

        results = [
            {
                "section": f"{row['citation__part']}.{row['citation__section__section_id']}",
                "subpart": row["citation__section__parent__subpart_id"],
                "html": row["banner_html"],
            }
            for row in rows
        ]

        return JsonResponse({"results": results})
