import unittest

import pytest

from regulations.models import SiteConfiguration


@pytest.mark.django_db
class SiteConfigurationTest(unittest.TestCase):
    def setUp(self):
        SiteConfiguration.objects.all().delete()

    def test_date_fields(self):
        site_config = SiteConfiguration.objects.create(pk=1)
        date_fields = [
            {
                'field_name': 'us_code_house_gov',
                'date_type': 'effective',
                'date': '2023',
            },
            {
                'field_name': 'ssa_gov_compilation',
                'date_type': 'amended',
                'date': 'Dec 2018',
            },
            {
                'field_name': 'statute_compilation',
                'date_type': 'effective',
                'date': 'Dec 2019',
            },
            {
                'field_name': 'us_code_annual',
                'date_type': 'effective',
                'date': 'Dec 2022',
            },
        ]

        for field in date_fields:
            field_name = field['field_name']
            date_type = field['date_type']
            date = field['date']

            # Set the date field values
            setattr(site_config, f"{field_name}_date_type", date_type)
            setattr(site_config, f"{field_name}_date", date)

            # Retrieve the date field values and assert
            retrieved_date_type = getattr(site_config, f"{field_name}_date_type")
            retrieved_date = getattr(site_config, f"{field_name}_date")

            self.assertEqual(retrieved_date_type, date_type)
            self.assertEqual(retrieved_date, date)

    def test_site_configuration_str(self):
        site_config = SiteConfiguration.get_solo()
        expected_str = 'Site Configuration'
        self.assertEqual(str(site_config), expected_str)

    def test_site_configuration_valid_date_type(self):
        site_config = SiteConfiguration.get_solo()
        site_config.full_clean()  # Should not raise any ValidationError

    def test_site_configuration_empty_date_type(self):
        site_config = SiteConfiguration.get_solo()
        site_config.full_clean()  # Should not raise any ValidationError
