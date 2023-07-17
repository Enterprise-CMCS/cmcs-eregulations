import unittest
import pytest
from regulations.models import SiteConfiguration
from django.core.exceptions import ValidationError

@pytest.mark.django_db
class SiteConfigurationTest(unittest.TestCase):
    def setUp(self):
        SiteConfiguration.objects.all().delete()

    def test_site_configuration_str(self):
        site_config = SiteConfiguration.objects.create(pk=2, date_type='effective', date='2023-07-10')
        expected_str = 'Effective 2023-07-10'
        self.assertEqual(str(site_config), expected_str)

    def test_site_configuration_valid_date_type(self):
        site_config = SiteConfiguration(date_type='effective')
        site_config.full_clean()  # Should not raise any ValidationError

    def test_site_configuration_empty_date_type(self):
        site_config = SiteConfiguration(date_type='')
        site_config.full_clean()  # Should not raise any ValidationError
