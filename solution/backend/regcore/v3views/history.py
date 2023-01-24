import datetime
import asyncio
import httpx

from rest_framework import viewsets
from rest_framework.response import Response

from regcore.serializers.history import HistorySerializer

async def compute_object(section, year, client):
    data = await client.head(f"https://www.govinfo.gov/link/cfr/{section['title']}/{section['part']}?sectionnum={section['section']}&year={year}&link-type=pdf")
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
    for future in asyncio.as_completed([compute_object(section_data, year, client) for year in range(1996, datetime.date.today().year + 1)]):
        yield loop.run_until_complete(future)

class SectionHistoryViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        title, part, section = [self.kwargs.get(i) for i in ["title", "part", "section"]]
        years = sorted([year for year in year_generator(title, part, section) if year != None], key=lambda year: year["year"])
        return Response(HistorySerializer(instance=years, many=True).data)
