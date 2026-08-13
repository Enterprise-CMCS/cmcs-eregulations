import unittest
from importlib import util
from pathlib import Path
import sys
import types


def _load_module():
    worker_dir = Path(__file__).resolve().parent.parent / "ecfr-worker"
    module_path = worker_dir / "transforms" / "__init__.py"

    package_name = "ecfr_worker_transform_pkg"
    package = types.ModuleType(package_name)
    package.__path__ = [str(worker_dir)]
    sys.modules[package_name] = package

    spec = util.spec_from_file_location(
        f"{package_name}.transforms",
        module_path,
        submodule_search_locations=[str(worker_dir / "transforms")],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ecfr worker transform module")
    module = util.module_from_spec(spec)
    sys.modules[f"{package_name}.transforms"] = module
    spec.loader.exec_module(module)
    return module


_module = _load_module()


class EcfrWorkerTransformTests(unittest.TestCase):
    def test_normalize_structure_for_upload_adds_parent_fields(self):
        raw = {
            "type": "title",
            "identifier": "42",
            "label": "Title &amp; Label",
            "children": [
                {
                    "type": "part",
                    "identifier": "400",
                    "descendant_range": "400.1 – 400.9",
                    "children": [
                        {
                            "type": "section",
                            "identifier": "400.1",
                            "children": [],
                        }
                    ],
                    "unexpected": "drop-me",
                }
            ],
        }

        normalized = _module.normalize_structure_for_upload(raw)

        self.assertEqual(normalized["identifier"], ["42"])
        self.assertEqual(normalized["label"], "Title & Label")
        self.assertEqual(normalized["parent"], [])
        self.assertEqual(normalized["parent_type"], "")

        part = normalized["children"][0]
        self.assertEqual(part["identifier"], ["400"])
        self.assertEqual(part["parent"], ["42"])
        self.assertEqual(part["parent_type"], "title")
        self.assertEqual(part["descendant_range"], ["400.1", "400.9"])
        self.assertNotIn("unexpected", part)

        section = part["children"][0]
        self.assertEqual(section["identifier"], ["400", "1"])
        self.assertEqual(section["parent"], ["400"])
        self.assertEqual(section["parent_type"], "part")

    def test_normalize_structure_for_upload_rejects_non_object(self):
        with self.assertRaisesRegex(_module.EcfrTransformError, "must be a JSON object"):
            _module.normalize_structure_for_upload([])

    def test_determine_part_depth(self):
        structure = {
            "type": "title",
            "identifier": ["42"],
            "children": [
                {
                    "type": "chapter",
                    "identifier": ["I"],
                    "children": [
                        {
                            "type": "subchapter",
                            "identifier": ["A"],
                            "children": [
                                {
                                    "type": "part",
                                    "identifier": ["400"],
                                    "children": [],
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        self.assertEqual(_module.determine_part_depth(structure, 400), 3)

    def test_determine_part_depth_missing_part(self):
        structure = {
            "type": "title",
            "identifier": ["42"],
            "children": [],
        }

        with self.assertRaisesRegex(_module.EcfrTransformError, "unable to locate part"):
            _module.determine_part_depth(structure, 400)

    def test_extract_sections_and_subparts(self):
        structure = {
            "type": "title",
            "identifier": ["42"],
            "children": [
                {
                    "type": "part",
                    "identifier": ["400"],
                    "children": [
                        {
                            "type": "section",
                            "identifier": ["400", "200"],
                            "reserved": False,
                        },
                        {
                            "type": "section",
                            "identifier": ["400", "201"],
                            "reserved": True,
                        },
                        {
                            "type": "subpart",
                            "identifier": ["B"],
                            "reserved": False,
                            "children": [
                                {
                                    "type": "section",
                                    "identifier": ["400", "202"],
                                    "reserved": False,
                                },
                                {
                                    "type": "subject_group",
                                    "children": [
                                        {
                                            "type": "section",
                                            "identifier": ["400", "203"],
                                            "reserved": False,
                                        },
                                        {
                                            "type": "section",
                                            "identifier": ["400", "204"],
                                            "reserved": True,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                }
            ],
        }

        sections, subparts = _module.extract_sections_and_subparts(structure, 400)

        self.assertEqual(
            sections,
            [
                {
                    "title": "42",
                    "part": "400",
                    "section": "200",
                }
            ],
        )
        self.assertEqual(len(subparts), 1)
        self.assertEqual(subparts[0]["title"], "42")
        self.assertEqual(subparts[0]["part"], "400")
        self.assertEqual(subparts[0]["subpart"], "B")
        self.assertEqual(
            subparts[0]["sections"],
            [
                {"title": "42", "part": "400", "section": "202"},
                {"title": "42", "part": "400", "section": "203"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
