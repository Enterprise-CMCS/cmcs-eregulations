from urllib.parse import urlparse

from django.conf import settings
from django.urls import reverse


def google_analytics(request):
    return {
        "GA_ID": settings.GA_ID
    }


def is_admin_user(request):
    return {
        "IS_ADMIN_USER": request.user.groups.filter(name='EREGS_ADMIN').exists()
    }


def site_root(request):
    url = urlparse(request.build_absolute_uri())
    path_parts = url.path.split("/")
    site_root = ""
    if len(path_parts) > 1 and url.netloc.endswith(".amazonaws.com"):
        site_root = path_parts[1]
    return {"SITE_ROOT": f"/{site_root}"}


def survey_url(request):
    return {
        "SURVEY_URL": settings.SURVEY_URL
    }


def demo_video_url(request):
    return {
        "DEMO_VIDEO_URL": settings.DEMO_VIDEO_URL
    }


def signup_url(request):
    return {
        "SIGNUP_URL": settings.SIGNUP_URL
    }


def automated_testing(request):
    return {
        "AUTOMATED_TEST": request.META.get("HTTP_X_AUTOMATED_TEST") == "true"
    }


def api_base(request):
    return {
        "API_BASE": f"{reverse('homepage')}{settings.API_BASE}"
    }


def deploy_number(request):
    return {
        "DEPLOY_NUMBER": settings.DEPLOY_NUMBER
    }
