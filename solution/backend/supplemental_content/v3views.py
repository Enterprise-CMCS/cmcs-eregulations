from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.exceptions import BadRequest
from django.db.models import Prefetch

from .models import (
    AbstractSupplementalContent,
    FederalRegisterDocument,
    AbstractCategory,
    Category,
    SubCategory,
)

from .views import SettingsAuthentication

from .v3serializers import (
    FederalRegisterDocumentCreateSerializer,
    AbstractCategorySerializer
)
from regcore.serializers import StringListSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AbstractCategory.objects.all().select_subclasses().select_related("subcategory__parent")
    serializer_class = AbstractCategorySerializer


class SupplementalContentViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        query = AbstractSupplementalContent.objects.all()


class FederalRegisterDocumentViewSet(viewsets.ModelViewSet):
    queryset = FederalRegisterDocument.objects.all()

    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def update(self, request, **kwargs):
        data = request.data
        frdoc, created = FederalRegisterDocument.objects.get_or_create(document_number=data["document_number"])
        data["id"] = frdoc.pk
        sc = self.get_serializer(frdoc, data=data)
        try:
            if sc.is_valid(raise_exception=True):
                sc.save()
                response = sc.validated_data
                return JsonResponse(response)
        except Exception as e:
            if created:
                frdoc.delete()
            raise e
    
    def get_queryset(self):
        return FederalRegisterDocument.objects.all().values_list("document_number", flat=True).distinct()

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return FederalRegisterDocumentCreateSerializer
        return StringListSerializer
