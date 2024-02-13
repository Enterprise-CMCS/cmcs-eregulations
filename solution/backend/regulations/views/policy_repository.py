from django.http import HttpResponsePermanentRedirect
from django.urls import reverse


def PolicyRepositoryView(request):
    redirect_string = '?' + request.GET.urlencode() if request.GET else ''
    response = HttpResponsePermanentRedirect(reverse('subjects') + redirect_string)
    return response
