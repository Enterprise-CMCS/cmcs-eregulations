import unittest
from importlib import util
from pathlib import Path


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "fr-worker" / "links.py"
    spec = util.spec_from_file_location("fr_worker_links", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load fr worker links module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load_module()


class CreateSectionsTests(unittest.TestCase):
    def test_valid(self):
        part_map = {"438": "42", "41": "45"}
        sections = _module.create_sections(["438.502", "41.118"], part_map)
        self.assertEqual(
            sections,
            [
                _module.LinkSection(title="42", part="438", section_id=502),
                _module.LinkSection(title="45", part="41", section_id=118),
            ],
        )

    def test_no_matching_title(self):
        result = _module.create_sections(["999.1"], {"438": "42"})
        self.assertEqual(result, [])

    def test_invalid_section_token(self):
        result = _module.create_sections(["no-dot", "438."], {"438": "42"})
        self.assertEqual(result, [])


class CreateSectionRangesTests(unittest.TestCase):
    def test_valid_range(self):
        part_map = {"438": "42"}
        ranges = _module.create_section_ranges(["438.502-438.700"], part_map)
        self.assertEqual(
            ranges,
            [_module.LinkSectionRange(title="42", part="438", first_sec=502, last_sec=700)],
        )

    def test_different_parts_skipped(self):
        part_map = {"438": "42", "41": "45"}
        ranges = _module.create_section_ranges(["438.502-41.118"], part_map)
        self.assertEqual(ranges, [])

    def test_invalid_range_token(self):
        result = _module.create_section_ranges(["438.502"], {"438": "42"})
        self.assertEqual(result, [])

    def test_no_matching_title_skipped(self):
        result = _module.create_section_ranges(["438.502-438.700"], {})
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
