from django.conf import settings
from django.http import HttpRequest
from django.test import TestCase

from cmcs_regulations.context_processors import custom_url


class CustomUrlContextProcessorTest(TestCase):
    def test_custom_url_match(self):
        request = HttpRequest()
        request.META['HTTP_HOST'] = 'regulations-pilot.cms.gov'

        settings.CUSTOM_URL = 'https://eregulations.cms.gov'

        context = custom_url(request)

        self.assertEqual(context['CUSTOM_URL'], 'https://eregulations.cms.gov')

    def test_custom_url_no_match(self):
        request = HttpRequest()
        request.META['HTTP_HOST'] = 'regulations-pilot.cms.gov'

        settings.CUSTOM_URL = 'https://regulations-pilot.cms.gov'

        context = custom_url(request)

        self.assertEqual(context['CUSTOM_URL'], 'https://regulations-pilot.cms.gov')
