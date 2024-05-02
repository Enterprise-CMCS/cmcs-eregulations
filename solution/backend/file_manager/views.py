
from django.conf import settings
from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponseRedirect
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.api import OpenApiQueryParameter
from common.constants import QUOTE_TYPES
from common.functions import establish_client
from common.mixins import PAGINATION_PARAMS
from content_search.models import ContentIndex
from file_manager.serializers.files import (
    AwsTokenSerializer,
    UploadedFileSerializer,
)
from file_manager.serializers.groupings import (
    AbstractRepositoryCategoryPolymorphicSerializer,
    MetaRepositoryCategorySerializer,
    RepositoryCategoryTreeSerializer,
    SubjectCountsSerializer,
    SubjectDetailsSerializer,
)
from file_manager.serializers.groups import (
    DivisionWithGroupSerializer,
    GroupWithDivisionSerializer,
)
from resources.models import AbstractLocation, AbstractResource
from resources.views.mixins import LocationExplorerViewSetMixin, LocationFiltererMixin, OptionalPaginationMixin

from .functions import get_upload_link
from .models import (
    AbstractRepoCategory,
    Division,
    Group,
    RepositoryCategory,
    RepositorySubCategory,
    Subject,
    UploadedFile,
)


@extend_schema(description="Retrieve a list of subjects.")
class SubjectViewset(viewsets.ReadOnlyModelViewSet):
    model = Subject

    def list(self, request):
        query = self.model.objects.all()

        # Only load "resource_type" and "id" to avoid loading the entire database's store of extracted text into memory at once.
        # Needed to prevent slow response times and massive memory spikes.
        index_prefetch = ContentIndex.objects.all().only("resource_type", "id")

        index_prefetch_internal = index_prefetch.filter(resource_type='internal').values_list('id', flat=True)
        index_prefetch_external = index_prefetch.filter(resource_type='external').values_list('id', flat=True)

        query = query.prefetch_related(
            Prefetch('content', queryset=index_prefetch))
        query = query.annotate(internal_content=Count('content', filter=Q(content__id__in=index_prefetch_internal)))
        query = query.annotate(external_content=Count('content', filter=Q(content__id__in=index_prefetch_external)))
        query = query.order_by('combined_sort')
        context = self.get_serializer_context()
        serializer = SubjectDetailsSerializer(query, many=True, context=context)
        return Response(serializer.data)


@extend_schema(description="Retrive a list of divisions and their associated groups.")
class DivisionViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = DivisionWithGroupSerializer

    def get_queryset(self):
        return Division.objects.all().prefetch_related(Prefetch("group", queryset=Group.objects.all()))


@extend_schema(description="Retrieve a list of groups and their associated divisions.")
class GroupViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupWithDivisionSerializer

    def get_queryset(self):
        return Group.objects.all().prefetch_related(Prefetch("divisions", queryset=Division.objects.all()))


class UploadedFileViewset(viewsets.ReadOnlyModelViewSet, LocationExplorerViewSetMixin, OptionalPaginationMixin):
    permission_classes = (IsAuthenticated,)
    model = UploadedFile
    location_filter_prefix = "locations__"
    pagination_class = OptionalPaginationMixin.pagination_class

    def make_headline(self, field, search_query, search_type):
        return SearchHeadline(
            field,
            SearchQuery(search_query, search_type=search_type, config="english"),
            start_sel='<span class="search-headline">',
            stop_sel='</span>',
            config="english",
            highlight_all=True,
        )

    def get_search_headlines(self, search_query, search_type):
        return {
            "document_name_headline": self.make_headline("document_name", search_query, search_type),
            "summary_headline": self.make_headline("summary", search_query, search_type),
        }

    def get_queryset(self):
        locations = self.request.GET.getlist("locations")
        subjects = self.request.GET.getlist("subjects")
        category = self.request.GET.getlist("category")
        search_query = self.request.GET.get("q")
        query = self.model.objects.all()
        q_obj = self.get_location_filter(locations)

        if q_obj:
            query = query.filter(q_obj)
        if subjects:
            query = query.filter(subjects__id__in=subjects)
        if category:
            query = query.filter(category__id=category)

        locations_prefetch = AbstractLocation.objects.all().select_subclasses()
        subjects_prefetch = Subject.objects.all()
        division_prefetch = Division.objects.all().prefetch_related(Prefetch("group", queryset=Group.objects.all()))

        query = query.prefetch_related(
            Prefetch("locations", queryset=locations_prefetch),
            Prefetch("subjects", queryset=subjects_prefetch),
            Prefetch("division", queryset=division_prefetch)).distinct()

        if search_query:
            (search_type, cover_density) = (
                ("phrase", True)
                if search_query.startswith(QUOTE_TYPES) and search_query.endswith(QUOTE_TYPES)
                else ("plain", False)
            )
            vector = SearchVector("document_name", weight="A", config="english") + \
                SearchVector("summary", weight="B", config="english") + \
                SearchVector("date", weight="C", config="english")
            query = query.annotate(
                rank=SearchRank(
                    vector,
                    SearchQuery(search_query, search_type=search_type, config="english"),
                    cover_density=cover_density,
                ),
                **self.get_search_headlines(search_query, search_type),
            )
            query = query.filter(Q(rank__gte=0.2) | Q(file_name__icontains=search_query))
        else:
            query = query.order_by('date', 'document_name')
        return query

    @extend_schema(
        description="Retrieve list of uploaded files",
        parameters=[
                    OpenApiQueryParameter("location_details",
                                          "Specify whether to show details of a location, or just the ID.",
                                          bool, False),
                    OpenApiQueryParameter("subjects",
                                          "Limit results to only resources found within these subjects. Use "
                                          "\"&subjects=X&subjects=Y\" for multiple.", int, False),
                    OpenApiQueryParameter("q",
                                          "Search for text within file metadata. Searches document_name, file name, "
                                          "date, and summary.", str, False),
                    ] + LocationExplorerViewSetMixin.PARAMETERS
    )
    def list(self, request):
        queryset = self.get_queryset()
        context = self.get_serializer_context()
        paginate = self.request.GET.get("paginate") != 'false'
        if paginate:
            queryset = self.paginate_queryset(queryset)
            serializer = UploadedFileSerializer(queryset, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        serializer = UploadedFileSerializer(queryset, many=True, context=context)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        queryset = UploadedFile.objects.all()
        id = kwargs.get("id")
        file = queryset.get(uid=id)
        serializer = UploadedFileSerializer(file, many=False)
        return Response(serializer.data)

    def generate_download_link(self, obj):
        s3_client = establish_client('s3')
        key = obj.get_key()
        params = {'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                  'Key': key,
                  'ResponseContentDisposition': f"inline;filename={obj.file_name}"}
        if obj.extension() == '.pdf':
            params['ResponseContentType'] = "application/pdf"
        return s3_client.generate_presigned_url('get_object',
                                                Params=params,
                                                ExpiresIn=20)

    def upload(self, request, *args, **kwargs):
        id = kwargs.get("file_id")
        file_name = kwargs.get("file_name")
        uploaded_file = None
        if id:
            uploaded_file = UploadedFile.objects.get(uid=id)
            uploaded_file.file_name = file_name
        elif file_name:
            uploaded_file = UploadedFile(file_name=file_name)
            uploaded_file.save()
        else:
            raise Exception("File name not provided")

        if uploaded_file:
            result = get_upload_link(uploaded_file.get_key())
            serializer = AwsTokenSerializer(result)
            return Response(serializer.data)

    @extend_schema(description="Download a piece of internal resource")
    def download(self, request, *args, **kwargs):
        queryset = UploadedFile.objects.all()
        id = kwargs.get("file_id")
        file = queryset.get(uid=id)

        url = self.generate_download_link(file)
        response = HttpResponseRedirect(url)
        return response


@extend_schema(
    description="Retrieve a flat list of all categories. Pagination is disabled by default.",
    parameters=OptionalPaginationMixin.PARAMETERS + PAGINATION_PARAMS + [
        OpenApiQueryParameter("parent_details", "Show details about each sub-category's parent, rather "
                              "than just the ID.", bool, False),
    ],
    responses=MetaRepositoryCategorySerializer.many(True),
)
class RepoCategoryViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    paginate_by_default = False
    serializer_class = AbstractRepositoryCategoryPolymorphicSerializer
    queryset = AbstractRepoCategory.objects.all().select_subclasses().prefetch_related(
        Prefetch("repositorysubcategory__parent", RepositorySubCategory.objects.all().order_by("order")),
    ).order_by("order")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["parent_details"] = self.request.GET.get("parent_details", "true").lower() == "true"
        return context


@extend_schema(
    description="Retrieve a top-down representation of repository categories, "
                "with each category containing zero or more sub-categories. "
                "Pagination is disabled by default.",
    parameters=OptionalPaginationMixin.PARAMETERS + PAGINATION_PARAMS,
)
class RepositoryCategoryTreeViewSet(OptionalPaginationMixin, viewsets.ReadOnlyModelViewSet):
    paginate_by_default = False
    queryset = RepositoryCategory.objects.all().select_subclasses().prefetch_related(
        Prefetch("sub_categories", RepositorySubCategory.objects.all().order_by("order")),
    ).order_by("order")
    serializer_class = RepositoryCategoryTreeSerializer


class TopSubjectsByLocationViewSet(LocationFiltererMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving top subjects based on location.
    Uses LocationFiltererMixin to apply location-based filters.
    """
    location_filter_prefix = "locations__"
    serializer_class = SubjectCountsSerializer

    def get_queryset(self):
        """
        Override the default queryset to filter and annotate based on locations,
        returning only the top 5 subjects by count.
        """
        locations = self.request.GET.getlist("locations")
        if not locations:
            return Subject.objects.none()

        # Fetch the 'top_x' parameter from the query parameters or use 5 as default
        top_x = int(self.request.GET.get("top_x", 5))
        min_count = int(self.request.GET.get("min_count", 1))
        resources = AbstractResource.objects.filter(self.get_location_filter(locations)).distinct().values_list('pk', flat=True)


        # Apply location filter to the Subject queryset
        query = Subject.objects.filter(resources__pk__in=resources)
        # Annotate each Subject with a count of primary keys and order by this count
        query = query.annotate(count=Count('pk')).filter(count__gte=min_count).order_by('-count')

        # Return only the top 5 subjects
        return query[:top_x]
