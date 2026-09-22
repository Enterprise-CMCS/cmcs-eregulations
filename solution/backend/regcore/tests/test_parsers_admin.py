from unittest.mock import Mock, patch

from django.contrib.admin.sites import AdminSite
from django.test import SimpleTestCase

from parsers.admin import ParserConfigurationAdmin
from parsers.models import EcfrParserResult, ParserConfiguration, PartConfiguration


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

    def test_save_formset_with_part_config_delete_invalidates_matching_results(self):
        model_admin = ParserConfigurationAdmin(ParserConfiguration, AdminSite())
        formset = Mock()
        formset.deleted_objects = [PartConfiguration(title=42, type="part", value="433")]

        filtered_parts = Mock()
        affected_parts = Mock()
        affected_parts.exists.return_value = True
        part_pairs_qs = Mock()
        part_pairs_qs.distinct.return_value = [(42, 433)]
        affected_parts.values_list.return_value = part_pairs_qs
        affected_parts.delete.return_value = (1, {"regcore.Part": 1})
        filtered_parts.distinct.return_value = affected_parts

        with (
            patch("parsers.admin.SingletonModelAdmin.save_formset", autospec=True) as mock_super,
            patch("parsers.admin.Part.objects.filter", return_value=filtered_parts),
            patch("parsers.admin.apps.is_installed", return_value=False),
            patch.object(EcfrParserResult.objects, "filter") as mock_result_filter,
            patch("parsers.admin.timezone.now", return_value="NOW") as mock_now,
            patch.object(ParserConfigurationAdmin, "message_user", autospec=True),
        ):
            mock_result_filter.return_value.update = Mock()
            model_admin.save_formset(
                request=Mock(),
                form=Mock(),
                formset=formset,
                change=True,
            )

        formset.save.assert_called_once_with(commit=False)
        self.assertEqual(mock_super.call_count, 1)
        self.assertEqual(mock_result_filter.call_count, 1)
        mock_now.assert_called_once_with()
        mock_result_filter.return_value.update.assert_called_once_with(invalidated_at="NOW")

    def test_save_formset_with_content_search_missing_contentindex_key_does_not_raise(self):
        model_admin = ParserConfigurationAdmin(ParserConfiguration, AdminSite())
        formset = Mock()
        formset.deleted_objects = [PartConfiguration(title=42, type="part", value="433")]

        filtered_parts = Mock()
        affected_parts = Mock()
        affected_parts.exists.return_value = True
        part_pairs_qs = Mock()
        part_pairs_qs.distinct.return_value = [(42, 433)]
        affected_parts.values_list.return_value = part_pairs_qs
        affected_parts.delete.return_value = (1, {"regcore.Part": 1})
        filtered_parts.distinct.return_value = affected_parts

        indexed_qs = Mock()
        indexed_qs.delete.return_value = (1, {"content_search.IndexedRegulationText": 1})

        with (
            patch("parsers.admin.SingletonModelAdmin.save_formset", autospec=True) as mock_super,
            patch("parsers.admin.Part.objects.filter", return_value=filtered_parts),
            patch("parsers.admin.apps.is_installed", return_value=True),
            patch.object(EcfrParserResult.objects, "filter") as mock_result_filter,
            patch("content_search.models.IndexedRegulationText.objects.filter", return_value=indexed_qs),
            patch("parsers.admin.timezone.now", return_value="NOW"),
            patch.object(ParserConfigurationAdmin, "message_user", autospec=True),
        ):
            mock_result_filter.return_value.update = Mock()

            model_admin.save_formset(
                request=Mock(),
                form=Mock(),
                formset=formset,
                change=True,
            )

        self.assertEqual(mock_super.call_count, 1)
