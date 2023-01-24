import datetime
import asyncio
import httpx

from rest_framework import viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from regcore.serializers.history import HistorySerializer
from .utils import OpenApiPathParameter

GOVINFO_YEAR_MIN = 1996
GOVINFO_LINK = "https://www.govinfo.gov/link/cfr/{}/{}?sectionnum={}&year={}&link-type=pdf"


async def check_year(section, year, client):
    data = await client.head(GOVINFO_LINK.format(section["title"], section["part"], section["section"], year))
    if data.status_code == 400:
        return None
    elif data.status_code == 302:
        link = data.headers["location"]
    else:
        link = None
    return {
        "year": str(year),
        "link": link,
    }


def year_generator(title, part, section):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = httpx.AsyncClient()
    section_data = {
        "title": title,
        "part": part,
        "section": section,
    }
    max_year = datetime.date.today().year + 1
    for future in asyncio.as_completed([check_year(section_data, year, client) for year in range(GOVINFO_YEAR_MIN, max_year)]):
        yield loop.run_until_complete(future)
    client.aclose()


@extend_schema(
    description="Retrieve a list of links to GovInfo PDFs for historical versions of a regulation section.",
    parameters=[
        OpenApiPathParameter("title", "The title containing the regulation section.", int),
        OpenApiPathParameter("part", "The part containing the regulation section.", int),
        OpenApiPathParameter("section", "The section to get historical versions of.", int),
    ]
)
class SectionHistoryViewSet(viewsets.ViewSet):
    serializer_class = HistorySerializer

    def list(self, request, *args, **kwargs):
        title, part, section = [self.kwargs.get(i) for i in ["title", "part", "section"]]
        years = sorted([year for year in year_generator(title, part, section) if year is not None], key=lambda year: year["year"])
        return Response(self.serializer_class(instance=years, many=True).data)
