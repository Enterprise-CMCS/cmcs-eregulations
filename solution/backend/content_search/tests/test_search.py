import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from common.test_functions.common_functions import get_paginated_data
from content_search.models import ContentIndex
from resources.models import FederalRegisterLink, InternalCategory, PublicCategory, PublicLink, Section, Subject
from resources.models.internal_resources import InternalFile


class SearchTest(TestCase):
    def check_exclusive_response(self, response, id):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_paginated_data(response)
        print(f"Data: {data}")
        self.assertEqual(data['results'][0]["resource"]["title"], self.internal_docs[id]["title"])

    def login(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test_user', password='test')  # noqa: S106
        self.client.force_authenticate(self.user)

    def clean_up(self):
        PublicLink.objects.all().delete()
        FederalRegisterLink.objects.all().delete()
        InternalFile.objects.all().delete()
        ContentIndex.objects.all().delete()
        PublicLink.objects.all().delete()
        PublicCategory.objects.all().delete()
        InternalCategory.objects.all().delete()

    def setUp(self):
        self.clean_up()
        self.internal_docs = []
        self.cfr_citations1 = Section.objects.create(title="42", part="433", section_id="1")
        self.cfr_citations2 = Section.objects.create(title="33", part="31", section_id="22")
        self.public_category = PublicCategory.objects.create(name='public test category')
        self.internal_category = InternalCategory.objects.create(name='internal test category')
        self.subject1 = Subject.objects.create()
        self.subject2 = Subject.objects.create()

        with open("content_search/tests/fixtures/public_links.json", "r") as f:
            for i, data in enumerate(json.load(f)):
                file = PublicLink.objects.create(**data)
                if i == 0:
                    file.cfr_citations.set([self.cfr_citations2])
                    file.subjects.set([self.subject2])
                    file.category = self.public_category
                    file.save()
                elif i == 1:  # Assign internal category for another item
                    file.cfr_citations.set([self.cfr_citations1])
                    file.subjects.set([self.subject1])
                    file.category = self.internal_category
                    file.save()

        with open("content_search/tests/fixtures/fr_docs.json", "r") as f:
            for i, data in enumerate(json.load(f)):
                file = FederalRegisterLink.objects.create(**data)
                if i == 0:
                    file.cfr_citations.set([self.cfr_citations2])
                    file.subjects.set([self.subject2])
                    file.category = self.public_category
                    file.save()
                elif i == 1:  # Assign internal category for another item
                    file.cfr_citations.set([self.cfr_citations1])
                    file.subjects.set([self.subject1])
                    file.category = self.internal_category
                    file.save()

        with open("content_search/tests/fixtures/internal_files.json", "r") as f:
            for i, data in enumerate(json.load(f)):
                self.internal_docs.append(data)
                file = InternalFile.objects.create(**data)
                if i == 0:
                    file.cfr_citations.set([self.cfr_citations2])
                    file.subjects.set([self.subject2])
                    file.category = self.public_category
                    file.save()
                elif i == 1:  # Assign internal category for another item
                    file.cfr_citations.set([self.cfr_citations1])
                    file.subjects.set([self.subject1])
                    file.category = self.internal_category
                    file.save()

    def test_no_query_not_logged_in(self):
        response = self.client.get("/v3/content-search?show_internal=true&show_regulations=false")
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_no_query_returns_400(self):
        self.login()
        response = self.client.get("/v3/content-search/?show_internal=false&show_regulations=false")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unapproved_is_hidden(self):
        PublicLink.objects.create(approved=False, title="Unapproved")
        response = self.client.get("/v3/content-search/?q=unapproved")
        data = get_paginated_data(response)
        self.assertEqual(data['count'], 0)

    def test_single_response_queries(self):
        self.login()
        response = self.client.get("/v3/content-search/?q=fire&show_internal=false&show_regulations=false")
        data = get_paginated_data(response)
        print(f"Data: {data}")
        self.assertEqual(data['count'], 1)
        response = self.client.get(r"/v3/content-search/?q='end%20fire'&show_internal=false&show_regulations=false")
        data = get_paginated_data(response)
        print(f"Data: {data}")
        self.assertEqual(data['count'], 0)
        response = self.client.get("/v3/content-search/?q='start%20fire'&show_internal=false&show_regulations=false")
        data = get_paginated_data(response)
        print(f"Data: {data}")
        self.assertEqual(data['count'], 1)
        response = self.client.get("/v3/content-search/?q=fire")
        data = get_paginated_data(response)
        print(f"Data: {data}")
        self.assertEqual(data['count'], 2)

    def test_multi_response_query(self):
        # This tests to ensure files are correctly *included* based on search terms
        self.login()
        response = self.client.get("/v3/content-search/?q=file")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_paginated_data(response)
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["results"][0]["resource"]["title"], self.internal_docs[0]["title"])
        self.assertEqual(data["results"][1]["resource"]["title"], self.internal_docs[2]["title"])
        response = self.client.\
            get("/v3/content-search/?q=fire&show_internal=false&show_regulations=false")
        data = get_paginated_data(response)
        self.assertEqual(data['count'], 1)
        response = self.client.get("/v3/content-search/?q=fire&show_public=false&show_regulations=false")
        data = get_paginated_data(response)
        self.assertEqual(data['count'], 1)
        data = get_paginated_data(response)
        response = self.client.get("/v3/content-search/?q=fire&show_regulations=false&page_size=2")
        data = get_paginated_data(response)
        self.assertEqual(data['count'], 2)

    def test_search_by_filename_variations(self):
        self.login()
        words = ["cheese", "pokemon"]
        for word in words:
            response = self.client.get(f"/v3/content-search/?show_internal=true&q={word}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = get_paginated_data(response)
            print(f"Data: {data}")
            self.assertIn(word, data['results'][0]['resource']['file_name'])

    def test_inclusive_citations_filter(self):
        self.login()
        response = self.client.get("/v3/content-search/?show_public=false&show_regulations=false&q=test&citations=42.433")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_paginated_data(response)
        self.assertEqual(data['count'], 0)

        response = self.client.get("/v3/content-search/?q=test&show_public=false&citations=42.433&citations=33.31")
        data = get_paginated_data(response)
        self.check_exclusive_response(response, 0)

    def test_inclusive_subject_filter(self):
        self.login()

        response = self.client.\
            get(f"/v3/content-search/?show_public=false&show_regulations=false&q=test&subjects={self.subject1.id}")
        data = get_paginated_data(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['count'], 0)

        response = self.client.get(
            f"/v3/content-search/?"
            f"show_public=false&"
            f"show_regulations=false&"
            f"q=test&"
            f"subjects={self.subject1.id}&"
            f"subjects={self.subject2.id}")
        self.check_exclusive_response(response, 0)

    def test_content_search(self):
        a = ContentIndex.objects.first()
        a.content = "dummy dummy dummy"
        a.save()
        self.login()
        response = self.client.get("/v3/content-search/?&q='dummy'")
        data = get_paginated_data(response)
        self.assertTrue("dummy" in data['results'][0]['content_headline'])

    # This test ensures that highlighting for multiple words in a document is working properly.
    # For example a search for "affordable care act" on a document should highlight the entire phrase, not just one word of it.
    def test_multiword_highlighting(self):
        a = ContentIndex.objects.first()
        a.name = "abc affordable xyz care 123 act"
        a.summary = "this is an affordable care act document"
        a.content = "this is an affordable document about the Affordable Care Act blah blah blah etc etc etc Care act"
        a.save()
        self.login()
        response = self.client.get("/v3/content-search/?q=affordable care act")
        data = get_paginated_data(response)

        expected = "this is an <span class='search-highlight'>affordable</span> document about the <span class='search-highlight"\
                   "'>Affordable</span> <span class='search-highlight'>Care</span> <span class='search-highlight'>Act</span> bla"\
                   "h blah blah etc etc etc <span class='search-highlight'>Care</span> <span class='search-highlight'>act</span>"
        self.assertEqual(expected, data["results"][0]["content_headline"])

        expected = "abc <span class='search-highlight'>affordable</span> xyz <span class='search-highlight'>care</span> 123 <spa"\
                   "n class='search-highlight'>act</span>"
        print(f"Data: {data['results'][0]}")
        self.assertEqual(expected, data["results"][0]["name_headline"])

        expected = "this is an <span class='search-highlight'>affordable</span> <span class='search-highlight'>care</span> <span"\
                   " class='search-highlight'>act</span> document"
        self.assertEqual(expected, data["results"][0]["summary_headline"])

    # Search for "reference" returns a file that does not have the word "reference" in its content field
    # So the content_headline field should be blank instead of the text of the content field.
    def test_no_highlight_blanking(self):
        self.login()
        response = self.client.get("/v3/content-search/?q=reference")
        data = get_paginated_data(response)
        print(f"Data: {data}")
        self.assertEqual(data["results"][0]["content_headline"], '')

    # If sorted by 'id', a search for 'fire' from fixture data will return two results with pk's 92 then 98.
    # We want the results sorted by rank, which if working properly will return the reverse: 98 then 92.
    def test_rank_sorting(self):
        self.login()
        response = self.client.get("/v3/content-search/?q=fire")
        data = get_paginated_data(response)
        results = data["results"]
        print(f"Results: {results}")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['resource']["title"], "Policy reference file fire fire fire")
        self.assertEqual(results[1]['resource']["title"], "But the worlds been burning since the worlds been turning")
