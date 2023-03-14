from django.conf import settings
from django.urls import reverse


def google_analytics(request):
    return {
        "GA_ID": settings.GA_ID
    }


def custom_url(request):
    return {
        "CUSTOM_URL": settings.CUSTOM_URL
    }


def survey_url(request):
    return {
        "SURVEY_URL": settings.SURVEY_URL
    }


def automated_testing(request):
    return {
        "AUTOMATED_TEST": request.META.get("HTTP_X_AUTOMATED_TEST") == "true"
    }


def api_base(request):
    return {
        "API_BASE": f"{reverse('homepage')}{settings.API_BASE}"
    }
