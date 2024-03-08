from django.http import HttpResponsePermanentRedirect
from django.urls import reverse


def ResourcesView(request):
    return HttpResponsePermanentRedirect(reverse('subjects'))
