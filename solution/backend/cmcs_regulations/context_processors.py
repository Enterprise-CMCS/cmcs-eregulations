from django.conf import settings
from django.urls import reverse


def google_analytics(request):
    return {
        "GA_ID": settings.GA_ID
    }


def is_valid_host(host):
    allowed_hosts = ['eregulations.cms.gov', 'static.eregulations.cms.gov']

    if host in allowed_hosts:
        return True

    return False


def custom_url(request):
    custom_url = settings.CUSTOM_URL
    host = request.get_host()

    if is_valid_host(host):
        custom_url = f'https://{host}/'
    else:
        pass

    return {'CUSTOM_URL': custom_url}


def survey_url(request):
    return {
        "SURVEY_URL": settings.SURVEY_URL
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
