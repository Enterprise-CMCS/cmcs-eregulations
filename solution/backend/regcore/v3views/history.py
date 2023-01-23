import datetime

from rest_framework import viewsets
from rest_framework.response import Response

from regcore.serializers.history import HistorySerializer

class SectionHistoryViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        years = []
        for year in range(1996, datetime.date.today().year + 1):
            years.append({
                "year": str(year),
                "link": "a-link",
            })
        return Response(HistorySerializer(instance=years, many=True).data)