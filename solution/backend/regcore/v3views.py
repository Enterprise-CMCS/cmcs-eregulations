from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from regcore.models import Title
from regcore.serializers import ContentsSerializer
from regcore.views import SettingsAuthentication

class ContentsViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = ContentsSerializer
    
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
