from django.conf import settings


def google_analytics(request):
    return {
        "GA_ID": settings.GA_ID
    }


def custom_url(request):
    return {
        "CUSTOM_URL": settings.CUSTOM_URL
    }


def eregs_url(request):
    return {
        "EREGS_URL": settings.EREGS_URL
    }


def automated_testing(request):
    return {
        "AUTOMATED_TEST": request.META.get("HTTP_X_AUTOMATED_TEST") == "true"
    }
