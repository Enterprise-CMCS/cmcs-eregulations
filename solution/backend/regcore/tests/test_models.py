
import json

from django.test import TestCase

from regcore.models import Part


class TestRegoreModels(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open("regcore/tests/fixtures/part.json") as f:
            doc = json.load(f)
        structure = {"type": "title", "children": [{"type:": "part", "label": 400, "children": ["part content"]}]}
        Part.objects.create(title='42', date="2020-06-30", last_updated="2022-09-21 08:36:45.735759",
                            depth=2, structure=structure, name=400, document=doc,
                            depth_stack={"depthstack": "stuff"})

    def test_get_toc(self):
        part = Part.objects.get(name=400)
        toc = part.toc
        self.assertEqual(toc, 'part content')
