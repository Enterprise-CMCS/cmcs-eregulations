import unittest
import pytest
from django.core.exceptions import ValidationError
from regulations.models import SiteConfiguration

@pytest.mark.django_db
class SiteConfigurationTest(unittest.TestCase):
    def test_site_configuration_str(self):
        SiteConfiguration.objects.all().delete()
        site_config = SiteConfiguration.objects.create(pk=2, date_type='effective', date='2023-07-10')
        expected_str = 'Effective 2023-07-10'
        self.assertEqual(str(site_config), expected_str)

    def test_site_configuration_blank_date_type(self):
        site_config = SiteConfiguration(date='')
        site_config.full_clean()  # Should not raise any ValidationError

    def test_site_configuration_valid_date_type(self):
        site_config = SiteConfiguration(date_type='effective')
        site_config.full_clean()  # Should not raise any ValidationError
