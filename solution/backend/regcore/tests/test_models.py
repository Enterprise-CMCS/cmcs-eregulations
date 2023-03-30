from django.test import TestCase
from regcore.models import ParserConfiguration, Part, TitleConfiguration
from regcore.search.models import Synonym
from regcore.search.models import create_search
import json

class TestRegoreModels(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open("regcore/tests/fixtures/part.json") as f:
            doc = json.load(f)
        structure = {"type": "title", "children": [{"type:": "part", "label": 400, "children": ["part content"]}]}
        Part.objects.create(title='42', date="2020-06-30", last_updated="2022-09-21 08:36:45.735759",
                            depth=2, structure=structure, name=400, document=doc,
                            depth_stack={"depthstack": "stuff"})
        TitleConfiguration.objects.create(title=50, subchapters="c, d", parts="40, 50",
                                          parser_config=ParserConfiguration.objects.get(id=1))
        s1 = Synonym.objects.create(isActive=True, baseWord="Syn1")
        s2, _ = Synonym.objects.get_or_create(isActive=True, baseWord="S2")
        s2.synonyms.set([s1])

    def test_get_toc(self):
        part = Part.objects.get(name=400)
        toc = part.toc
        self.assertEqual(toc, 'part content')

    def test_title_config_check(self):
        title = TitleConfiguration.objects.get(title=50)
        self.assertEqual(title.__str__(), 'Title 50 config')
        self.assertEqual(title.parts, "40, 50")

    def test_Synonym_create(self):
        s1 = Synonym.objects.get(baseWord="Syn1")
        self.assertTrue(s1.synonyms.exists())

    def test_create_search(self):
        part = Part.objects.get(name=400)
        searchIndexes = create_search(part, part.document, [], parent=None)
        self.assertEqual(searchIndexes[0].part_number, "400")
        self.assertEqual(len(searchIndexes), 2)
        self.assertEqual(searchIndexes[1].section_number, "10")
        self.assertEqual(searchIndexes[0].section_string, "400.1")
