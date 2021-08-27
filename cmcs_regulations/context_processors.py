from django.conf import settings


def google_analytics(request):
    return {
        "GA_ID": settings.GA_ID,
    }


def automated_testing(request):
    return {
        "AUTOMATED_TEST": settings.AUTOMATED_TEST,
    }
