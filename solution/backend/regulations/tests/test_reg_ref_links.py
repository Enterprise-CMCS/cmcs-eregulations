import json

from django.template import Context, Template
from django.test import SimpleTestCase


class LinkRegRefsTestCase(SimpleTestCase):
    def test_link_reg_refs(self):
        with open("regulations/tests/fixtures/reg_ref_link_tests.json", "r") as f:
            test_values = json.load(f)

        config = {}

        for test in test_values:
            template = Template("{% load link_reg_refs %}{% link_reg_refs paragraph link_config as text %}{{ text | safe }}")
            context = Context({
                "paragraph": test["input"],
                "link_config": config,
            })
            self.assertEqual(template.render(context), test["expected"])
