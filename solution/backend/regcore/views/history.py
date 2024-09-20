import asyncio
import datetime

import httpx
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from regcore.serializers.history import HistorySerializer

from .utils import OpenApiPathParameter

HTTPX_TIMEOUT = 10
GOVINFO_YEAR_MIN = 1996
GOVINFO_LINK = "https://www.govinfo.gov/link/cfr/{}/{}?sectionnum={}&year={}&link-type=pdf"


async def get_year_data(section, year, client):
    return await client.head(GOVINFO_LINK.format(section["title"], section["part"], section["section"], year))


async def check_year(section, year, client):
    try:
        data = await get_year_data(section, year, client)
    except httpx.TimeoutException:
        return None
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


async def get_years(title, part, section):
    max_year = datetime.date.today().year + 1
    section_data = {
        "title": title,
        "part": part,
        "section": section,
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(HTTPX_TIMEOUT)) as client:
        years = await asyncio.gather(*[check_year(section_data, year, client) for year in range(GOVINFO_YEAR_MIN, max_year)])
    return [year for year in years if year is not None]


@extend_schema(
    tags=["regcore/metadata"],
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
        years = asyncio.run(get_years(title, part, section))
        return Response(self.serializer_class(instance=years, many=True).data)
