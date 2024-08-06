from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest, ValidationError
from django.http import Http404
from django.urls import reverse
from django.views.generic.base import RedirectView

from resources.models import AbstractResource, InternalFile
from resources.utils import establish_client


class InternalFileDownloadViewSet(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        uid = kwargs.get("uid")
        if not uid:
            raise BadRequest("The URL parameter 'uid' must be specified.")
        try:
            file = InternalFile.objects.get(uid=uid)
            return self._get_download_link(file)
        except ValidationError:
            raise BadRequest(f"'{uid}' is not a valid UID.")
        except InternalFile.DoesNotExist:
            raise Http404(f"A file matching UID '{uid}' does not exist.")

    def _get_download_link(self, file):
        s3_client = establish_client('s3')
        params = {
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": file.key,
            "ResponseContentDisposition": f"inline;filename={file.file_name}",
        }

        if file.extension == ".pdf":
            params["ResponseContentType"] = "application/pdf"

        return s3_client.generate_presigned_url("get_object", Params=params, ExpiresIn=20)


class ResourceEditViewSet(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        resource_id = kwargs.get("id")
        if not resource_id:
            raise BadRequest("The URL parameter 'id' must be specified.")
        try:
            resource = AbstractResource.objects.select_subclasses().get(id=resource_id)
            return reverse(f"admin:{resource._meta.app_label}_{resource._meta.model_name}_change", args=[resource_id])
        except AbstractResource.DoesNotExist:
            raise Http404(f"A resource matching ID {resource_id} does not exist.")
