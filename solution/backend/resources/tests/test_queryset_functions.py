from django.test import TestCase
from django.db.models import F, Case, When
from resources.models import FederalRegisterDocument, FederalRegisterDocumentGroup, AbstractResource, SupplementalContent
from resources.views.mixins import FRDocGroupingMixin
from datetime import datetime, timedelta


class TestMixinFunctions(TestCase):
    def setUp(self):
        FederalRegisterDocumentGroup.objects.create(id=1)
        FederalRegisterDocumentGroup.objects.create(id=2)
        FederalRegisterDocumentGroup.objects.create(id=3)
        a = FederalRegisterDocumentGroup.objects.get(id=1)
        b = FederalRegisterDocumentGroup.objects.get(id=2)
        c = FederalRegisterDocumentGroup.objects.get(id=3)
        today = datetime.today().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
        twodaysago = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')
        FederalRegisterDocument.objects.create(id=1, group=a, date=today)
        FederalRegisterDocument.objects.create(id=2, group=a, date=twodaysago)
        FederalRegisterDocument.objects.create(id=3, group=b, date=yesterday)
        FederalRegisterDocument.objects.create(id=4, group=c, date=today)
        FederalRegisterDocument.objects.create(id=5, group=b, date=today)
        SupplementalContent.objects.create(id=6, date=today)

    def get_annotated_date(self):
        return Case(
            When(supplementalcontent__isnull=False, then=F("supplementalcontent__date")),
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__date")),
            default=None,
        )

    def get_annotated_group(self):
        return Case(
            When(federalregisterdocument__isnull=False, then=F("federalregisterdocument__group")),
            default=-1*F("pk"),
        )

    def test_get_id_one_groups(self):
        docs = AbstractResource.objects.filter(id__in=[1, 2]).annotate(group_annotated=self.get_annotated_group())
        mixin = FRDocGroupingMixin()
        ids = mixin.get_final_ids(docs)
        self.assertEqual([1], ids)

    def test_get_id_two_groups(self):
        docs = AbstractResource.objects.filter(id__in=[1, 5]).annotate(group_annotated=self.get_annotated_group())
        mixin = FRDocGroupingMixin()
        ids = mixin.get_final_ids(docs)
        self.assertEqual([1, 5], ids)

    def test_get_id_two_groups_different_return(self):
        docs = AbstractResource.objects.filter(id__in=[1, 3]).annotate(group_annotated=self.get_annotated_group())
        mixin = FRDocGroupingMixin()
        ids = mixin.get_final_ids(docs)
        self.assertEqual([1, 5], ids)

    def test_get_id_two_groups_share_group(self):
        docs = AbstractResource.objects.filter(id__in=[1, 3, 5]) \
                                       .annotate(group_annotated=self.get_annotated_group()) \
                                       .annotate(date=self.get_annotated_date())

        mixin = FRDocGroupingMixin()
        ids = mixin.get_final_ids(docs)
        self.assertEqual([1, 5], ids)

    def test_get_id_two_groups_share_group_one_sup(self):
        docs = AbstractResource.objects.filter(id__in=[1, 3, 5, 6]) \
                                       .annotate(group_annotated=self.get_annotated_group()) \
                                       .annotate(date=self.get_annotated_date())

        mixin = FRDocGroupingMixin()
        ids = mixin.get_final_ids(docs)
        self.assertEqual([1, 5, 6], ids)

    def test_one_sup(self):
        docs = AbstractResource.objects.filter(id__in=[6]) \
                                       .annotate(group_annotated=self.get_annotated_group()) \
                                       .annotate(date=self.get_annotated_date())

        mixin = FRDocGroupingMixin()
        ids = mixin.get_final_ids(docs)
        self.assertEqual([6], ids)

    def test_get_all_resources(self):
        docs = AbstractResource.objects.all().annotate(group_annotated=self.get_annotated_group()) \
                                             .annotate(date=self.get_annotated_date())
        mixin = FRDocGroupingMixin()
        ids = mixin.get_final_ids(docs)
        ids.sort()
        self.assertEqual([1, 4, 5, 6], ids)
