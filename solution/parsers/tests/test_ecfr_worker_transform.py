import unittest
from importlib import util
from pathlib import Path


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "ecfr-worker" / "transform.py"
    spec = util.spec_from_file_location("ecfr_worker_transform", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ecfr worker transform module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load_module()


class EcfrWorkerTransformTests(unittest.TestCase):
    def test_determine_part_depth(self):
        structure = {
            "type": "title",
            "identifier": "42",
            "children": [
                {
                    "type": "chapter",
                    "identifier": "I",
                    "children": [
                        {
                            "type": "subchapter",
                            "identifier": "A",
                            "children": [
                                {
                                    "type": "part",
                                    "identifier": "400",
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
            "identifier": "42",
            "children": [],
        }

        with self.assertRaisesRegex(_module.EcfrTransformError, "unable to locate part"):
            _module.determine_part_depth(structure, 400)

    def test_extract_sections_and_subparts(self):
        structure = {
            "type": "title",
            "identifier": "42",
            "children": [
                {
                    "type": "part",
                    "identifier": "400",
                    "children": [
                        {
                            "type": "section",
                            "identifier": "400.200",
                            "reserved": False,
                        },
                        {
                            "type": "section",
                            "identifier": "400.201",
                            "reserved": True,
                        },
                        {
                            "type": "subpart",
                            "identifier": "B",
                            "reserved": False,
                            "children": [
                                {
                                    "type": "section",
                                    "identifier": "400.202",
                                    "reserved": False,
                                },
                                {
                                    "type": "subject_group",
                                    "children": [
                                        {
                                            "type": "section",
                                            "identifier": "400.203",
                                            "reserved": False,
                                        },
                                        {
                                            "type": "section",
                                            "identifier": "400.204",
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
