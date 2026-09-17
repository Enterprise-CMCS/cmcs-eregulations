from unittest.mock import Mock, patch

from django.contrib.admin.sites import AdminSite
from django.test import SimpleTestCase

from parsers.admin import ParserConfigurationAdmin
from parsers.models import ParserConfiguration


class ParserConfigurationAdminTests(SimpleTestCase):
    def test_save_formset_without_part_config_deletes_does_not_delete_parts(self):
        model_admin = ParserConfigurationAdmin(ParserConfiguration, AdminSite())
        formset = Mock()
        formset.deleted_objects = []

        with (
            patch("parsers.admin.SingletonModelAdmin.save_formset", autospec=True) as mock_super,
            patch("parsers.admin.Part.objects.filter", autospec=True) as mock_part_filter,
        ):
            model_admin.save_formset(
                request=Mock(),
                form=Mock(),
                formset=formset,
                change=True,
            )

        mock_part_filter.assert_not_called()
        formset.save.assert_called_once_with(commit=False)
        self.assertEqual(mock_super.call_count, 1)
