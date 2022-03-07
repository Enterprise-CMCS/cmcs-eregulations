from rest_framework import viewsets

from regcore.models import Title

class ContentsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Title.objects.all()
    serializer_class = ContentsSerializer
