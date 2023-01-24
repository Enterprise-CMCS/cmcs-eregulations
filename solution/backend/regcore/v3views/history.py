import datetime
import asyncio
import httpx

from rest_framework import viewsets
from rest_framework.response import Response

from regcore.serializers.history import HistorySerializer


GOVINFO_YEAR_MIN = 1996
GOVINFO_LINK = "https://www.govinfo.gov/link/cfr/{}/{}?sectionnum={}&year={}&link-type=pdf"


async def check_year(section, year, client):
    data = await client.head(GOVINFO_LINK.format(section["title"], section["part"], section["section"], year))
    if data.status_code != 302:
        return None
    return {
        "year": str(year),
        "link": data.headers["location"],
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


class SectionHistoryViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        title, part, section = [self.kwargs.get(i) for i in ["title", "part", "section"]]
        years = sorted([year for year in year_generator(title, part, section) if year is not None], key=lambda year: year["year"])
        return Response(HistorySerializer(instance=years, many=True).data)
