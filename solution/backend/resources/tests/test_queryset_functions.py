from datetime import datetime, timedelta

from django.db.models import Case, F, OuterRef, Subquery, When
from django.test import TestCase

from resources.models import (
    AbstractResource,
    FederalRegisterLink,
    PublicLink,
    ResourceGroup,
)


class TestMixinFunctions(TestCase):
    def setUp(self):
        a = ResourceGroup.objects.create(id=1)
        b = ResourceGroup.objects.create(id=2)
        c = ResourceGroup.objects.create(id=3)
        today = datetime.today().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
        twodaysago = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')
        FederalRegisterLink.objects.create(id=1, group=a, date=today, url='site2 url')
        FederalRegisterLink.objects.create(id=2, group=a, date=twodaysago, url='site1 url')
        FederalRegisterLink.objects.create(id=3, group=b, date=yesterday, url='site3 url')
        FederalRegisterLink.objects.create(id=4, group=c, date=today)
        FederalRegisterLink.objects.create(id=5, group=b, date=today)
        PublicLink.objects.create(id=6, date=today)

    # this is the function used by the resource explorer viewset but cant figure out how to just copy it.
    def get_annotated_group(self):
        return Case(
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__group")),
            default=-1 * F("pk"),
        )

    def get_final_ids(self, id_query):
        fr_groups = []
        ids = []

        for i in id_query:
            if i.group_annotated is None or i.group_annotated < 0:
                ids.append(i.id)
            elif i.group_annotated not in fr_groups:
                fr_groups.append(i.group_annotated)

        if fr_groups:
            newest = FederalRegisterLink.objects.filter(group_id=OuterRef('pk')).order_by('-date')
            groups = ResourceGroup.objects \
                .annotate(newest_doc=Subquery(newest.values('id')[:1])) \
                .filter(id__in=fr_groups) \
                .values_list('newest_doc', flat=True)
            ids = list(groups) + ids
        return ids

    def test_get_id_one_groups(self):
        docs = AbstractResource.objects.filter(id__in=[1, 2]).annotate(group_annotated=self.get_annotated_group())
        ids = self.get_final_ids(docs)
        self.assertEqual([1], ids)

    def test_get_id_two_groups(self):
        docs = AbstractResource.objects.filter(id__in=[1, 5]).annotate(group_annotated=self.get_annotated_group())
        ids = self.get_final_ids(docs)
        self.assertEqual([1, 5], ids)

    def test_get_id_two_groups_different_return(self):
        docs = AbstractResource.objects.filter(id__in=[1, 3]).annotate(group_annotated=self.get_annotated_group())
        ids = self.get_final_ids(docs)
        self.assertEqual([1, 5], ids)

    def test_get_id_two_groups_share_group(self):
        docs = AbstractResource.objects.filter(id__in=[1, 3, 5]) \
                                       .annotate(group_annotated=self.get_annotated_group())

        ids = self.get_final_ids(docs)
        self.assertEqual([1, 5], ids)

    def test_get_id_two_groups_share_group_one_sup(self):
        docs = AbstractResource.objects.filter(id__in=[1, 3, 5, 6]) \
                                       .annotate(group_annotated=self.get_annotated_group())

        ids = self.get_final_ids(docs)
        self.assertEqual([1, 5, 6], ids)

    def test_one_sup(self):
        docs = AbstractResource.objects.filter(id__in=[6]) \
                                       .annotate(group_annotated=self.get_annotated_group())

        ids = self.get_final_ids(docs)
        self.assertEqual([6], ids)

    def test_get_all_resources(self):
        docs = AbstractResource.objects.all().annotate(group_annotated=self.get_annotated_group())
        ids = self.get_final_ids(docs)
        ids.sort()
        self.assertEqual([1, 4, 5, 6], ids)
