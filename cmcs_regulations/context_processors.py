from django.conf import settings


def google_analytics(request):
    return {
        "GA_ID": settings.GA_ID,
    }


def automated_testing(request):
    return {
        "AUTOMATED_TEST": request.META.get("HTTP_X_AUTOMATED_TEST") == "true"
    }
