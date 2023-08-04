import json
from datetime import datetime, timedelta
from itertools import chain

from django.test import TestCase
from rest_framework.exceptions import NotFound

from resources.models import (
    FederalRegisterDocument,
    FederalRegisterDocumentGroup,
    SupplementalContent,
)
from resources.views.resources import ResourceSearchViewSet


class TestMixinFunctions(TestCase):
    def setUp(self):
        a = FederalRegisterDocumentGroup.objects.create(id=1)
        b = FederalRegisterDocumentGroup.objects.create(id=2)
        c = FederalRegisterDocumentGroup.objects.create(id=3)
        today = datetime.today().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
        twodaysago = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')
        FederalRegisterDocument.objects.create(id=1, group=a, date=today, url='www.site2url.com')
        FederalRegisterDocument.objects.create(id=2, group=a, date=twodaysago, url='www.site1url.com')
        FederalRegisterDocument.objects.create(id=3, group=b, date=yesterday, url='www.site3url.com')
        FederalRegisterDocument.objects.create(id=4, group=c, date=today)
        FederalRegisterDocument.objects.create(id=5, group=b, date=today)
        SupplementalContent.objects.create(id=6, date=today)
        SupplementalContent.objects.create(id=7, date=yesterday, url='www.site4url.com#1')
        SupplementalContent.objects.create(id=8, date=yesterday, url='www.site4url.com#2')

    def test_search_gov_ordering(self):
        urls = ['www.site1url.com', 'www.site2url.com', 'www.site3url.com']
        resources = FederalRegisterDocument.objects.filter(id__in=[1, 2, 3])
        test_view_set = ResourceSearchViewSet()
        ordered_resources = test_view_set.sort_by_url_list(urls, resources)
        ordered_resources = list(chain.from_iterable(ordered_resources))
        self.assertEqual(ordered_resources[1], FederalRegisterDocument.objects.get(id=1))
        self.assertEqual(ordered_resources[0], FederalRegisterDocument.objects.get(id=2))
        self.assertEqual(ordered_resources[2], FederalRegisterDocument.objects.get(id=3))

    # since the rss feed is prod data, dev environments might have less resources
    def test_missing_gov_resource(self):
        urls = ['www.site1url.com', 'www.site2url.com', 'www.site3url.com']
        resources = FederalRegisterDocument.objects.filter(id__in=[1, 2])
        test_view_set = ResourceSearchViewSet()
        ordered_resources = test_view_set.sort_by_url_list(urls, resources)
        self.assertEqual(len(ordered_resources), 2)

    def test_format_gov_results(self):
        with open("resources/tests/fixtures/gov_info_success.json") as f:
            gov_info = json.load(f)
        test_view_set = ResourceSearchViewSet()
        test_view_set.format_gov_results(gov_info)
        results = test_view_set.gov_results
        self.assertEqual(results['total'], 3)
        self.assertEqual(results['results'][0]['name'], 'site1')
        self.assertEqual(results['results'][0]['url'], 'www.site1url.com')
        self.assertEqual(results['results'][0]['snippet'], '...site1 snippet')

    def test_format_gov_results_zero_results(self):
        with open("resources/tests/fixtures/gov_info_zero.json") as f:
            gov_info = json.load(f)
        test_view_set = ResourceSearchViewSet()
        self.assertRaises(NotFound, test_view_set.format_gov_results, gov_info)

    def test_append_snippet(self):
        test_view_set = ResourceSearchViewSet()
        resources = list(FederalRegisterDocument.objects.filter(id__in=[1, 2, 3]))
        with open("resources/tests/fixtures/url_snippet_dict.json") as f:
            urls = json.load(f)
        ordered_resources = test_view_set.sort_by_url_list(urls.keys(), resources)
        resources = list(chain.from_iterable(ordered_resources))
        results = test_view_set.append_snippet(resources, urls)
        num = 1
        for r in results:
            self.assertEqual(f'...site{num} snippet', r.snippet)
            num = num + 1

    def test_append_snippet_dup(self):
        test_view_set = ResourceSearchViewSet()
        resources = list(SupplementalContent.objects.filter(id__in=[7, 8]))
        with open("resources/tests/fixtures/url_snippet_dict_page.json") as f:
            urls = json.load(f)

        ordered_resources = test_view_set.sort_by_url_list(urls.keys(), resources)
        resources = list(chain.from_iterable(ordered_resources))
        results = test_view_set.append_snippet(resources, urls)

        num = 4
        page = 1
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(f'...site{num} snippet', r.snippet)
            self.assertEqual(f'www.site{num}url.com#{page}', r.url)
            page = page + 1

    def test_queryset(self):
        with open("resources/tests/fixtures/url_snippet_dict.json") as f:
            urls = json.load(f)
        test_view_set = ResourceSearchViewSet()
        queryset = test_view_set.get_queryset(urls.keys())
        self.assertEqual(len(queryset), 3)

    def test_result_object(self):
        test_view_set = ResourceSearchViewSet()
        test_view_set.gov_results["total"] = 40
        url = "http://localhost:8000/search?&page="
        obj = test_view_set.result_object(url + "1", "records", 1)
        self.assertEqual(obj["count"], 40)
        self.assertIsNone(obj['next'])
        self.assertIsNone(obj['previous'])
        test_view_set.gov_results["total"] = 60
        obj = test_view_set.result_object(url + "1", "records", 1)
        self.assertEqual(obj["count"], 60)
        self.assertEqual(obj['next'], url + "2")
        self.assertIsNone(obj['previous'])
        obj = test_view_set.result_object(url + "2", "records", 2)
        self.assertIsNone(obj['next'])
        self.assertEqual(obj['previous'], url + "1")
