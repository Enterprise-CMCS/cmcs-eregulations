import unittest
from regulations.models import SiteConfiguration


class SiteConfigurationTest(unittest.TestCase):
    def test_site_configuration_str(self):
        site_config = SiteConfiguration.objects.create(date_type='effective', date='2023-07-10')
        expected_str = 'Effective 2023-07-10'
        self.assertEqual(str(site_config), expected_str)

    def test_site_configuration_reverse(self):
        expected_date_type = 'effective'
        expected_date = '2023-07-10'
        site_config = SiteConfiguration.objects.create(date_type=expected_date_type, date=expected_date)
        parsed_site_config = SiteConfiguration.objects.get(pk=site_config.pk)
        self.assertEqual(parsed_site_config.date_type, expected_date_type)
        self.assertEqual(parsed_site_config.date, expected_date)

    #def test_site_configuration_reverse_invalid(self):


if __name__ == '__main__':
    unittest.main()