from django.http import HttpResponsePermanentRedirect
from django.urls import reverse


def OBBBAView(request):
    return HttpResponsePermanentRedirect(reverse('pl_119_21'))
