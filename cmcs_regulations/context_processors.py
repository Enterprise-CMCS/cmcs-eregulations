from django.conf import settings


def google_analytics(request):
    return {
        "GA_ID": settings.GA_ID,
    }
