from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from regcore.models import Title

class ContentsViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = ContentsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
