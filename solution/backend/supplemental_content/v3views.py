import json
from django.http import JsonResponse

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import AbstractCategory, Section, SupplementalContent
from .views import SettingsAuthentication
from .serializers import CreateSupplementalContentSerializer


class SupplementalContentViewSet(viewsets.ModelViewSet):
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CreateSupplementalContentSerializer
    queryset = SupplementalContent.objects.all()

    def update(self, request, **kwargs):
        data = request.data

        # same docket number means update existing record
        supplemental_content, _ = SupplementalContent.objects.get_or_create(docket_number=data["docket_number"])

        # slip this into the data for validation
        data["id"] = supplemental_content.pk

        # serialize the data for validation
        sc = self.get_serializer(supplemental_content, data=data)

        # save if valid
        if sc.is_valid():
            sc.save()
            response = sc.validated_data

        # return an error otherwise
        else:
            response = {"error": sc.errors}
        return JsonResponse(response)


