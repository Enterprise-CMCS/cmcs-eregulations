from django.test import TestCase


class RegcoreViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        return

    def test_url_exist(self):
        response = self.client.get("/v3/toc")
        self.assertEqual(response.status_code, 200)
