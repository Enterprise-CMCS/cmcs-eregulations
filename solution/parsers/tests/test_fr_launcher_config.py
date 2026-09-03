import unittest
from importlib import util
from pathlib import Path
from unittest.mock import Mock, patch


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "fr-launcher" / "frlaunch_config.py"
    spec = util.spec_from_file_location("fr_launcher_config", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load frlaunch_config module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load_module()
EregsConfigError = _module.EregsConfigError
FrTarget = _module.FrTarget
expand_fr_targets = _module.expand_fr_targets
fetch_subchapter_part_numbers = _module.fetch_subchapter_part_numbers


class FrLauncherConfigTests(unittest.TestCase):
    def test_expand_fr_targets_part_passthrough(self):
        parser_config = {
            "parts": [
                {
                    "title": 42,
                    "type": "part",
                    "value": "400",
                    "upload_fr_docs": True,
                }
            ]
        }

        targets = expand_fr_targets(parser_config)

        self.assertEqual(targets, [FrTarget(title_number=42, part_number=400)])

    def test_expand_fr_targets_skips_disabled_parts(self):
        parser_config = {
            "parts": [
                {
                    "title": 42,
                    "type": "part",
                    "value": "400",
                    "upload_fr_docs": False,
                }
            ]
        }

        targets = expand_fr_targets(parser_config)

        self.assertEqual(targets, [])

    def test_expand_fr_targets_mixed_enabled_and_disabled(self):
        parser_config = {
            "parts": [
                {"title": 42, "type": "part", "value": "400", "upload_fr_docs": True},
                {"title": 42, "type": "part", "value": "401", "upload_fr_docs": False},
                {"title": 42, "type": "part", "value": "402", "upload_fr_docs": True},
            ]
        }

        targets = expand_fr_targets(parser_config)

        self.assertEqual(
            targets,
            [FrTarget(42, 400), FrTarget(42, 402)],
        )

    @patch.object(_module, "fetch_subchapter_part_numbers", return_value=[400, 401])
    def test_expand_fr_targets_subchapter_expansion(self, mock_fetch):
        parser_config = {
            "parts": [
                {
                    "title": 42,
                    "type": "subchapter",
                    "value": "IV-C",
                    "upload_fr_docs": True,
                }
            ]
        }

        targets = expand_fr_targets(parser_config)

        self.assertEqual(
            targets,
            [FrTarget(42, 400), FrTarget(42, 401)],
        )
        mock_fetch.assert_called_once_with(
            title_number=42,
            chapter="IV",
            subchapter="C",
            timeout=60,
            base_url=_module.ECFR_V1_BASE_URL,
        )

    def test_expand_fr_targets_dedupes(self):
        parser_config = {
            "parts": [
                {"title": 42, "type": "part", "value": "400", "upload_fr_docs": True},
                {"title": 42, "type": "part", "value": "400", "upload_fr_docs": True},
            ]
        }

        targets = expand_fr_targets(parser_config)

        self.assertEqual(targets, [FrTarget(42, 400)])

    def test_expand_fr_targets_requires_parts_array(self):
        with self.assertRaisesRegex(EregsConfigError, "parts array"):
            expand_fr_targets({})

    def test_expand_fr_targets_missing_upload_fr_docs(self):
        parser_config = {
            "parts": [
                {"title": 42, "type": "part", "value": "400"},
            ]
        }

        with self.assertRaisesRegex(EregsConfigError, "upload_fr_docs"):
            expand_fr_targets(parser_config)

    def test_expand_fr_targets_invalid_subchapter_value(self):
        parser_config = {
            "parts": [
                {
                    "title": 42,
                    "type": "subchapter",
                    "value": "invalid",
                    "upload_fr_docs": True,
                }
            ]
        }

        with self.assertRaisesRegex(EregsConfigError, "CHAPTER-SUBCHAPTER"):
            expand_fr_targets(parser_config)

    def test_expand_fr_targets_invalid_title_type(self):
        parser_config = {
            "parts": [
                {
                    "title": "42",
                    "type": "part",
                    "value": "400",
                    "upload_fr_docs": True,
                }
            ]
        }

        with self.assertRaisesRegex(EregsConfigError, r"title must be a positive integer"):
            expand_fr_targets(parser_config)

    @patch("requests.get")
    def test_fetch_subchapter_part_numbers(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "type": "title",
            "children": [
                {
                    "type": "chapter",
                    "children": [
                        {
                            "type": "subchapter",
                            "children": [
                                {"type": "part", "identifier": "400"},
                                {"type": "part", "identifier": "401"},
                            ],
                        }
                    ],
                }
            ],
        }
        mock_get.return_value = response

        part_numbers = _module.fetch_subchapter_part_numbers(
            title_number=42,
            chapter="IV",
            subchapter="C",
            timeout=60,
            base_url=_module.ECFR_V1_BASE_URL,
        )

        self.assertEqual(part_numbers, [400, 401])


if __name__ == "__main__":
    unittest.main()
