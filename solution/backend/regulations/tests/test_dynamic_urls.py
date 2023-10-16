import unittest
from django.template import Template, Context

class CustomTemplateTagUnitTest(unittest.TestCase):
    def test_get_domain_request_match(self):
        # Create a template with the custom template tag
        template_code = '{% load dynamic_urls %}{% get_domain request CUSTOM_URL %}'
        template = Template(template_code)

        # Create a context with the necessary variables
        context = Context(
            {'request': self.mock_request('eregulations.cms.gov'), 'CUSTOM_URL': 'https://custom-url.com'})

        # Render the template with the context
        rendered_template = template.render(context)

        # Define the expected output based on the custom template tag's behavior
        expected_output = 'https://eregulations.cms.gov/'

        # Assert that the rendered template contains the expected output
        self.assertIn(expected_output, rendered_template)

    def test_get_domain_request_no_match(self):
        # Create a template with the custom template tag
        template_code = '{% load dynamic_urls %}{% get_domain request CUSTOM_URL %}'
        template = Template(template_code)

        # Create a context with the necessary variables
        context = Context(
            {'request': self.mock_request('regulations-pilot.cms.gov'), 'CUSTOM_URL': 'https://custom-url.com'})

        # Render the template with the context
        rendered_template = template.render(context)

        # Define the expected output based on the custom template tag's behavior
        expected_output = 'https://custom-url.com'  # Should not change for 'regulations-pilot.cms.gov'

        # Assert that the rendered template contains the expected output
        self.assertIn(expected_output, rendered_template)

    def mock_request(self, host):
        class MockRequest:
            def get_host(self):
                return host

        return MockRequest()