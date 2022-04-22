from django.http import JsonResponse

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import SupplementalContent
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
        supplemental_content, created = SupplementalContent.objects.get_or_create(document_number=data["document_number"])

        # slip this into the data for validation
        data["id"] = supplemental_content.pk

        # serialize the data for validation
        sc = self.get_serializer(supplemental_content, data=data)

        # save if valid
        try:
            if sc.is_valid(raise_exception=True):
                sc.save()
                response = sc.validated_data
                return JsonResponse(response)
        except Exception as e:
            # If this was created earlier, delete it as it should nto have been created.
            if created:
                supplemental_content.delete()
            raise e
