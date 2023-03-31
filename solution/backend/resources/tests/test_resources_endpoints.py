from django.test import TestCase
from resources.models import FederalRegisterDocument, FederalRegisterDocumentGroup, Section
from datetime import datetime, timedelta


class TestMixinFunctions(TestCase):
    def setUp(self):
        s1 = Section.objects.create(title=1, part=1, section_id=1)
        s2 = Section.objects.create(title=1, part=1, section_id=2)
        g1 = FederalRegisterDocumentGroup.objects.create(id=1)
        today = datetime.today().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
        twodaysago = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')
        f1 = FederalRegisterDocument.objects.create(id=1, group=g1, date=today)
        f1.locations.set([s1, s2])
        f1.save()
        f2 = FederalRegisterDocument.objects.create(id=2, group=g1, date=twodaysago)
        f2.locations.set([s1, s2])
        f2.save()
        f3 = FederalRegisterDocument.objects.create(id=3, group=g1, date=yesterday, approved=False)
        f3.locations.set([s1, s2])
        f3.save()

    def test_duplicate_groups(self):
        # If groups are duplicated, then len(response.data) will be greater than 1
        # This is because all 3 created docs have the same locations
        response = self.client.get("/v3/resources/?locations=1.1.1&locations=1.1.2&paginate=false")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_unapproved_showing(self):
        response = self.client.get("/v3/resources/?locations=1.1.1&locations=1.1.2&paginate=false")
        for i in response.data:
            self.assertEqual(i["approved"], True)
            if "related_docs" in i:
                for j in i["related_docs"]:
                    self.assertEqual(j["approved"], True)
