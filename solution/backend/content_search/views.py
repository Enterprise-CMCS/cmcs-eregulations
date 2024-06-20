import json

import requests
from django.conf import settings
from django.db.models import F, Prefetch, Q
from django.http import HttpResponseBadRequest
from django.core.exceptions import BadRequest
from django.shortcuts import redirect
from django.urls import reverse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import OpenApiParameter

from common.auth import SettingsAuthentication
from common.functions import establish_client
from common.mixins import CitationFiltererMixin

from resources.models import (
    AbstractCategory,
    AbstractCitation,
    AbstractResource,
    Subject,
)
from .models import ContentIndex
from .serializers import ContentUpdateSerializer, ContentSearchSerializer

from common.mixins import ViewSetPagination


@extend_schema(
    description="Retrieve list of uploaded files",
    parameters=[
        OpenApiParameter(
            name="subjects",
            required=False,
            type=int,
            description="Limit results to only resources found within these subjects. Subjects are referenced by ID, not name. "
                        "Use \"&subjects=1&subjects=2\" for multiple.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="categories",
            required=False,
            type=int,
            description="Limit results to only resources found within these categories. Categories are referenced by ID, not "
                        "name. Use \"&categories=1&categories=2\" for multiple.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="q",
            required=True,
            type=str,
            description="Search for this text within public and internal resources, and regulation text. "
                        "Fields searched depends on the underlying data type.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="show_public",
            required=False,
            type=str,
            description="Show ('true') or hide ('false') public resources, including Federal Register and other public links. "
                        "Default is true.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="show_internal",
            required=False,
            type=str,
            description="Show ('true') or hide ('false') internal resources, including files and internal links. "
                        "Default is true.",
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="show_regulations",
            required=False,
            type=str,
            description="Show ('true') or hide ('false') regulation text, including sections and appendices. "
                        "Default is true.",
            location=OpenApiParameter.QUERY,
        ),
    ] #+ LocationFiltererMixin.PARAMETERS + PAGINATION_PARAMS
)
class ContentSearchViewSet(CitationFiltererMixin, viewsets.ReadOnlyModelViewSet):
    model = ContentIndex
    serializer_class = ContentSearchSerializer
    citation_filter_prefix = "resource__cfr_citations__"
    pagination_class = ViewSetPagination

    def get_boolean_parameter(self, param, default):
        value = self.request.GET.get(param)
        if not value:
            return default
        value = value.lower().strip()
        if value in ("true", "t", "y", "yes", "1"):
            return True
        elif value in ("false", "f", "n", "no", "0"):
            return False
        raise BadRequest(f"Parameter '{param}' has an invalid value: '{value}'.")

    def get_queryset(self):
        citations = self.request.GET.getlist("citations")
        subjects = self.request.GET.getlist("subjects")
        categories = self.request.GET.getlist("categories")
        show_public = self.get_boolean_parameter("show_public", True)
        show_internal = self.get_boolean_parameter("show_internal", True)
        show_regulations = self.get_boolean_parameter("show_regulations", True)

        # /v4/content-search/?q=asdf&show_public&citations=42.
        # /v4/resources/?citations=42...

        search_query = self.request.GET.get("q")
        if not search_query:
            raise BadRequest("A search query is required; provide 'q' parameter in the query string.")

        query = ContentIndex.objects.all()

        # Filter inclusively by citations if this array exists
        citation_filter = self.get_citation_filter(citations)
        if citation_filter:
            query = query.filter(citation_filter)

        # Filter by subject pks if subjects array is present
        if subjects:
            query = query.filter(resource__subjects__pk__in=subjects)
        
        # Filter by categories (both parent and subcategories) if the categories array is present
        if categories:
            query = query.filter(
                Q(resource__category__pk__in=categories) |
                Q(resource__category__abstractpubliccategory__publicsubcategory__parent__pk__in=categories) |
                Q(resource__category__abstractinternalcategory__internalsubcategory__parent__pk__in=categories)
            )

        # Filter by public, internal, and regulation text
        if not show_public:
            query = query.exclude(resource__abstractpublicresource__isnull=False)
        if not show_internal or not self.request.user.is_authenticated:
            query = query.exclude(resource__abstractinternalresource__isnull=False)
        if not show_regulations:
            query = query.exclude(reg_text__isnull=False)

        # Perform search and headline generation
        query = query.search(search_query)
        ranked_results = [i.pk for i in self.paginate_queryset(query)]
        query = ContentIndex.objects.filter(pk__in=ranked_results).generate_headlines(search_query)

        # Prefetch all related data
        query = query.prefetch_related(
            Prefetch("resource", AbstractResource.objects.select_subclasses().prefetch_related(
                Prefetch("cfr_citations", AbstractCitation.objects.select_subclasses()),
                Prefetch("category", AbstractCategory.objects.select_subclasses()),
                Prefetch("subjects", Subject.objects.all()),
            )),
        )

        return query


class PostContentTextViewset(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SettingsAuthentication]

    @extend_schema(
        description="Adds text to the content of an index.",
        request=ContentUpdateSerializer,
        responses={200: ContentUpdateSerializer}
    )
    def post(self, request, *args, **kwargs):
        post_data = request.data
        id = post_data['id']
        text = post_data['text']
        index = ContentIndex.objects.get(uid=id)
        index.content = text
        index.save()
        return Response(data=f'Index was updated for {index.doc_name_string}')


class InvokeTextExtractorViewset(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Post to the lambda function",
    )
    def get(self, request, *args, **kwargs):
        uid = kwargs.get("content_id")
        fr_doc_id = kwargs.get("fr_doc_id")

        index = ContentIndex.objects.get(uid=uid)
        if not index:
            return Response({'message': "Index does not exist"})
        extract_url = index.extract_url

        if fr_doc_id:
            try:
                # doc = FederalRegisterDocument.objects.get(id=fr_doc_id)
                doc = None
                response = requests.get(
                    f"https://www.federalregister.gov/api/v1/documents/{doc.document_number}.json",
                    timeout=20,
                )
                response.raise_for_status()
                content = json.loads(response.content)
                extract_url = content["raw_text_url"]
                doc.raw_text_url = extract_url
                doc.save()
                index.extract_url = extract_url
                index.ignore_robots_txt = True
                index.save()
            except Exception:
                return Response({"message": "Failed to fetch the raw text URL."})

        if not settings.USE_LOCAL_TEXTRACT:
            post_url = request.build_absolute_uri(reverse("post-content"))
        else:
            post_url = "http://host.docker.internal:8000" + reverse("post-content")

        json_object = {
            'id': uid,
            'uri': index.extract_url,
            'ignore_robots_txt': index.ignore_robots_txt,
            'post_url': post_url,
            'auth': {
                "type": "basic-env",
                "username": "HTTP_AUTH_USER",
                "password": "HTTP_AUTH_PASSWORD",
            },
        }
        if index.file:
            try:
                json_object['uri'] = index.file.get_key()
                json_object['backend'] = 's3'
                # The lambda already has permissions to access the S3 bucket.  Only on a local run do we pass the keys.
                if settings.USE_LOCAL_TEXTRACT:
                    json_object["aws"] = {
                                            "aws_access_key_id": settings.S3_AWS_ACCESS_KEY_ID,
                                            "aws_secret_access_key": settings.S3_AWS_SECRET_ACCESS_KEY,
                                            "aws_storage_bucket_name": settings.AWS_STORAGE_BUCKET_NAME,
                                            'use_lambda': False,
                                            'aws_region': 'us-east-1'
                                        }
                else:
                    json_object["aws"] = {
                                            'use_lambda': True,
                                            "aws_storage_bucket_name": settings.AWS_STORAGE_BUCKET_NAME,
                                        }
            except ValueError:
                json_object['backend'] = 'web'

        if settings.USE_LOCAL_TEXTRACT:
            # return Response(json_object)
            docker_url = 'http://host.docker.internal:8001/'
            resp = requests.post(
                docker_url,
                data=json.dumps(json_object),
                timeout=60,
            )
            resp.raise_for_status()
        else:
            if settings.TEXT_EXTRACTOR_ARN:
                textract_arn = settings.TEXT_EXTRACTOR_ARN
            else:
                textract_arn = settings.TEXTRACT_ARN
            lambda_client = establish_client('lambda')
            resp = lambda_client.invoke(FunctionName=textract_arn,
                                        InvocationType='Event',
                                        Payload=json.dumps(json_object))
        return Response(data={'response': resp})


class EditContentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="redirects to a resource of an index.",
    )
    def get(self, request, *args, **kwargs):
        id = kwargs.get("resource_id")
        index = ContentIndex.objects.get(id=id)
        obj = None

        if index.file is not None:
            obj = index.file

        elif index.supplemental_content is not None:
            obj = index.supplemental_content

        elif index.fr_doc is not None:
            obj = index.fr_doc

        if obj is not None:
            url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
            return redirect(url)
        else:
            return HttpResponseBadRequest("Invalid index - no associated file, supplemental content, or fr_doc.")
