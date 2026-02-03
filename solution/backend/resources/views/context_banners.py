from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from cmcs_regulations.utils import ViewSetPagination
from resources.models import (
    AbstractCitation,
    SectionContextBanner,
)
from resources.serializers import (
    ContextBannerSerializer,
)


class ContextBannersViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = ViewSetPagination
    serializer_class = ContextBannerSerializer

    def get_queryset(self):
        try:
            title = int(self.request.GET.get("title"))
            part = int(self.request.GET.get("part"))
        except (TypeError, ValueError):
            raise ValidationError("Both 'title' and 'part' parameters must be provided as integers.")

        subpart = self.request.GET.get("subpart")
        section = self.request.GET.get("section")  # e.g., "75.104" or "104"

        qs = SectionContextBanner.objects.filter(is_active=True, citation__title=title, citation__part=part)

        # If a section is provided, narrow to that section only
        if section:
            # Normalize: allow "104" or "75.104"
            try:
                section_id = int(str(section).split(".")[-1])
                qs = qs.filter(citation__section__section_id=section_id)
            except ValueError:
                section_id = None

        elif subpart:
            # Otherwise, if a subpart is provided, show banners for that subpart
            qs = qs.filter(citation__section__parent__subpart_id=subpart)

        qs = qs.prefetch_related(Prefetch("citation", AbstractCitation.objects.select_subclasses()))

        return qs
