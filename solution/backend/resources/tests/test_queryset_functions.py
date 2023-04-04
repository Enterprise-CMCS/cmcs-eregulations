from datetime import datetime, timedelta
from django.test import TestCase
from django.db.models import F, Case, When

from resources.views.mixins import FRDocGroupingMixin
from resources.models import (
    FederalRegisterDocument,
    FederalRegisterDocumentGroup,
    AbstractResource,
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
        FederalRegisterDocument.objects.create(id=1, group=a, date=today, url='site2')
        FederalRegisterDocument.objects.create(id=2, group=a, date=twodaysago, url='site1')
        FederalRegisterDocument.objects.create(id=3, group=b, date=yesterday, url='site3')
        FederalRegisterDocument.objects.create(id=4, group=c, date=today)
        FederalRegisterDocument.objects.create(id=5, group=b, date=today)
        SupplementalContent.objects.create(id=6, date=today)
        self.FRDocGroupingMixin = FRDocGroupingMixin()

    # this is the function used by the resource explorer viewset but cant figure out how to just copy it.
    def get_annotated_group(self):
        return Case(
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__group")),
            default=-1*F("pk"),
        )

    def test_get_id_one_groups(self):
        docs = AbstractResource.objects.filter(id__in=[1, 2]).annotate(group_annotated=self.get_annotated_group())
        ids = self.FRDocGroupingMixin.get_final_ids(docs)
        self.assertEqual([1], ids)

    def test_get_id_two_groups(self):
        docs = AbstractResource.objects.filter(id__in=[1, 5]).annotate(group_annotated=self.get_annotated_group())
        ids = self.FRDocGroupingMixin.get_final_ids(docs)
        self.assertEqual([1, 5], ids)

    def test_get_id_two_groups_different_return(self):
        docs = AbstractResource.objects.filter(id__in=[1, 3]).annotate(group_annotated=self.get_annotated_group())
        ids = self.FRDocGroupingMixin.get_final_ids(docs)
        self.assertEqual([1, 5], ids)

    def test_get_id_two_groups_share_group(self):
        docs = AbstractResource.objects.filter(id__in=[1, 3, 5]) \
                                       .annotate(group_annotated=self.get_annotated_group())

        ids = self.FRDocGroupingMixin.get_final_ids(docs)
        self.assertEqual([1, 5], ids)

    def test_get_id_two_groups_share_group_one_sup(self):
        docs = AbstractResource.objects.filter(id__in=[1, 3, 5, 6]) \
                                       .annotate(group_annotated=self.get_annotated_group())

        ids = self.FRDocGroupingMixin.get_final_ids(docs)
        self.assertEqual([1, 5, 6], ids)

    def test_one_sup(self):
        docs = AbstractResource.objects.filter(id__in=[6]) \
                                       .annotate(group_annotated=self.get_annotated_group())

        ids = self.FRDocGroupingMixin.get_final_ids(docs)
        self.assertEqual([6], ids)

    def test_get_all_resources(self):
        docs = AbstractResource.objects.all().annotate(group_annotated=self.get_annotated_group())
        ids = self.FRDocGroupingMixin.get_final_ids(docs)
        ids.sort()
        self.assertEqual([1, 4, 5, 6], ids)

    def test_search_gov_ordering(self):
        urls = ['site1', 'site2', 'site3']
        resources = FederalRegisterDocument.objects.filter(id__in=[1, 2, 3])
        test_view_set = ResourceSearchViewSet()
        ordered_resources = test_view_set.sort_by_url_list(urls, resources)
        self.assertEqual(ordered_resources[1], FederalRegisterDocument.objects.get(id=1))
        self.assertEqual(ordered_resources[0], FederalRegisterDocument.objects.get(id=2))
        self.assertEqual(ordered_resources[2], FederalRegisterDocument.objects.get(id=3))

    # since the rss feed is prod data, dev environments might have less resources
    def test_missing_gov_resource(self):
        urls = ['site1', 'site2', 'site3']
        resources = FederalRegisterDocument.objects.filter(id__in=[1, 2])
        test_view_set = ResourceSearchViewSet()
        ordered_resources = test_view_set.sort_by_url_list(urls, resources)
        self.assertEqual(len(ordered_resources), 2)
