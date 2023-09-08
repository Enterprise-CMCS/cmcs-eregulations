
import json

from django.test import TestCase

from regcore.models import Part
from regcore.search.models import SearchIndexQuerySet, Synonym, create_search


class TestRegoreModels(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open("regcore/tests/fixtures/part.json") as f:
            doc = json.load(f)
        structure = {"type": "title", "children": [{"type:": "part", "label": 400, "children": ["part content"]}]}
        Part.objects.create(title='42', date="2020-06-30", last_updated="2022-09-21 08:36:45.735759",
                            depth=2, structure=structure, name=400, document=doc,
                            depth_stack={"depthstack": "stuff"})

        s1 = Synonym.objects.create(isActive=True, baseWord="Syn1")
        s2, _ = Synonym.objects.get_or_create(isActive=True, baseWord="S2")
        s2.synonyms.set([s1])

    def test_get_toc(self):
        part = Part.objects.get(name=400)
        toc = part.toc
        self.assertEqual(toc, 'part content')

    def test_Synonym_create(self):
        s1 = Synonym.objects.get(baseWord="Syn1")
        self.assertTrue(s1.synonyms.exists())

    def test_create_search(self):
        part = Part.objects.get(name=400)
        searchIndexes = create_search(part, part.document, [], parent=None)
        self.assertEqual(searchIndexes[0].part_number, "400")
        self.assertEqual(len(searchIndexes), 3)
        self.assertEqual(searchIndexes[1].section_number, "10")
        self.assertEqual(searchIndexes[0].section_string, "400.1")
        self.assertEqual(searchIndexes[2].section_string, "Appendix to Subpart F of Part 441")

    def test_search_type(self):
        si = SearchIndexQuerySet()
        query = "This is a non-quoted search"
        si.search_configuration(query)
        self.assertEqual(si.search_type, "plain")
        query = '"This is a phrase search"'
        si.search_configuration(query)
        self.assertEqual(si.search_type, "phrase")
        query = '“This is a phrase search”'
        si.search_configuration(query)
        self.assertEqual(si.search_type, "phrase")
        si = SearchIndexQuerySet()
        query = '“This is a plain search'
        si.search_configuration(query)
        self.assertEqual(si.search_type, "plain")
        query = '“This is a phrase search"'
        si.search_configuration(query)
        self.assertEqual(si.search_type, "phrase")
