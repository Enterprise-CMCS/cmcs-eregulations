import unittest
from importlib import util
from pathlib import Path


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "ecfr-launcher" / "ecfr_versions.py"
    spec = util.spec_from_file_location("ecfr_launcher_versions", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ecfr_versions module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ecfr_versions = _load_module()
EcfrVersionsError = _ecfr_versions.EcfrVersionsError
latest_issue_dates_by_part = _ecfr_versions.latest_issue_dates_by_part


class EcfrLauncherVersionsTests(unittest.TestCase):
    def test_latest_issue_dates_by_part_uses_latest_issue_date(self):
        payload = {
            "content_versions": [
                {
                    "part": "400",
                    "issue_date": "2024-01-01",
                    "date": "2024-01-01",
                    "removed": False,
                },
                {
                    "part": "400",
                    "issue_date": "2024-03-15",
                    "date": "2024-03-15",
                    "removed": False,
                },
                {
                    "part": "401",
                    "issue_date": "2024-02-20",
                    "date": "2024-02-20",
                    "removed": False,
                },
            ]
        }

        self.assertEqual(
            latest_issue_dates_by_part(payload),
            {
                "400": "2024-03-15",
                "401": "2024-02-20",
            },
        )

    def test_latest_issue_dates_by_part_ignores_removed_entries(self):
        payload = {
            "content_versions": [
                {
                    "part": "400",
                    "issue_date": "2024-01-01",
                    "removed": False,
                },
                {
                    "part": "400",
                    "issue_date": "2024-06-01",
                    "removed": True,
                },
            ]
        }

        self.assertEqual(latest_issue_dates_by_part(payload), {"400": "2024-01-01"})

    def test_latest_issue_dates_by_part_falls_back_to_date(self):
        payload = {
            "content_versions": [
                {
                    "part": "400",
                    "date": "2024-05-01",
                    "removed": False,
                },
                {
                    "part": "400",
                    "issue_date": "2024-04-01",
                    "removed": False,
                },
            ]
        }

        self.assertEqual(latest_issue_dates_by_part(payload), {"400": "2024-05-01"})

    def test_latest_issue_dates_by_part_ignores_invalid_entries(self):
        payload = {
            "content_versions": [
                {
                    "part": "400",
                    "issue_date": "not-a-date",
                    "removed": False,
                },
                {
                    "part": "   ",
                    "issue_date": "2024-01-01",
                    "removed": False,
                },
                "invalid",
            ]
        }

        self.assertEqual(latest_issue_dates_by_part(payload), {})

    def test_latest_issue_dates_by_part_requires_content_versions(self):
        with self.assertRaisesRegex(EcfrVersionsError, "content_versions"):
            latest_issue_dates_by_part({})


if __name__ == "__main__":
    unittest.main()
