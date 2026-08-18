import unittest
from importlib import util
from pathlib import Path
import sys
import types


def _load_modules():
    worker_dir = Path(__file__).resolve().parent.parent / "ecfr-worker"
    normalize_path = worker_dir / "xml_parser" / "normalize.py"
    models_path = worker_dir / "xml_parser" / "models.py"

    package_name = "ecfr_worker_xml_normalize_pkg"
    package = types.ModuleType(package_name)
    package.__path__ = [str(worker_dir)]
    sys.modules[package_name] = package

    xml_parser_package = types.ModuleType(f"{package_name}.xml_parser")
    xml_parser_package.__path__ = [str(worker_dir / "xml_parser")]
    sys.modules[f"{package_name}.xml_parser"] = xml_parser_package

    models_spec = util.spec_from_file_location(f"{package_name}.xml_parser.models", models_path)
    if models_spec is None or models_spec.loader is None:
        raise RuntimeError("Unable to load ecfr worker xml_parser.models module")
    models_module = util.module_from_spec(models_spec)
    sys.modules[f"{package_name}.xml_parser.models"] = models_module
    models_spec.loader.exec_module(models_module)

    normalize_spec = util.spec_from_file_location(f"{package_name}.xml_parser.normalize", normalize_path)
    if normalize_spec is None or normalize_spec.loader is None:
        raise RuntimeError("Unable to load ecfr worker xml_parser.normalize module")
    normalize_module = util.module_from_spec(normalize_spec)
    sys.modules[f"{package_name}.xml_parser.normalize"] = normalize_module
    normalize_spec.loader.exec_module(normalize_module)

    return models_module, normalize_module


_models, _module = _load_modules()
PartNode = _models.PartNode


class EcfrWorkerXmlNormalizeTests(unittest.TestCase):
    def test_normalize_part_minimal(self):
        part = PartNode(title_number=42, part_number=400, node_type="PART", label=["400"], title="Part 400")

        normalized = _module.normalize_part_for_eregs(part)

        self.assertEqual(
            normalized,
            {
                "node_type": "PART",
                "label": ["400"],
                "title": "Part 400",
                "children": [],
                "authority": None,
                "source": None,
                "editorial_note": None,
            },
        )

    def test_normalize_part_drops_unknown_keys_recursively(self):
        part = PartNode(
            title_number=42,
            part_number=400,
            node_type="PART",
            label=["400"],
            title="Part 400",
            children=[
                {
                    "node_type": "SECTION",
                    "label": ["400", "1"],
                    "title": "Sec. 400.1",
                    "children": [
                        {
                            "node_type": "Paragraph",
                            "text": "(a) First paragraph",
                            "label": ["400", "1", "a"],
                            "marker": ["a"],
                            "unknown": "drop-me",
                        },
                        {
                            "node_type": "Image",
                            "src": "/graphics/ER18OC21.004.gif",
                            "debug": True,
                        },
                        {
                            "node_type": "MYSTERY",
                            "foo": "bar",
                            "children": [{"node_type": "Citation", "content": "<I>X</I>", "extra": 1}],
                        },
                    ],
                    "extra": "remove",
                }
            ],
            authority={"node_type": "Authority", "header": "Authority:", "content": "42 U.S.C.", "x": 1},
            source={"node_type": "Source", "header": "Source:", "content": "90 FR", "x": 2},
            editorial_note={"node_type": "EdNote", "header": "Editorial Note:", "content": "Note", "x": 3},
        )

        normalized = _module.normalize_part_for_eregs(part)

        section = normalized["children"][0]
        paragraph = section["children"][0]
        image = section["children"][1]
        mystery = section["children"][2]
        nested_citation = mystery["children"][0]

        self.assertNotIn("extra", section)
        self.assertNotIn("unknown", paragraph)
        self.assertNotIn("debug", image)
        self.assertNotIn("foo", mystery)
        self.assertNotIn("extra", nested_citation)
        self.assertEqual(mystery, {"node_type": "MYSTERY", "children": [{"node_type": "Citation", "content": "<I>X</I>"}]})
        self.assertEqual(normalized["authority"], {"node_type": "Authority", "header": "Authority:", "content": "42 U.S.C."})

    def test_normalize_part_coerces_malformed_values_to_defaults(self):
        part = PartNode(
            title_number=42,
            part_number=400,
            node_type="PART",
            label=["400"],
            title="Part 400",
            children=[
                {
                    "node_type": "Paragraph",
                    "text": None,
                    "label": ["a", "", 1],
                    "marker": "not-a-list",
                },
                {
                    "node_type": "EffectiveDateNote",
                    "header": None,
                    "content": 123,
                },
            ],
            authority={"node_type": "Authority", "header": None, "content": 123},
            source="not-a-dict",
            editorial_note={"node_type": "not-ednote", "header": "x", "content": "y"},
        )

        normalized = _module.normalize_part_for_eregs(part)

        self.assertEqual(normalized["node_type"], "PART")
        self.assertEqual(normalized["label"], ["400"])
        self.assertEqual(normalized["title"], "Part 400")
        self.assertEqual(normalized["children"][0], {"node_type": "Paragraph", "text": "", "label": ["a"], "marker": []})
        self.assertEqual(normalized["children"][1], {"node_type": "EffectiveDateNote", "header": "", "content": ""})
        self.assertEqual(normalized["authority"], {"node_type": "Authority", "header": "", "content": ""})
        self.assertIsNone(normalized["source"])
        self.assertIsNone(normalized["editorial_note"])

    def test_normalize_container_nodes_enforce_schema(self):
        part = PartNode(
            title_number=42,
            part_number=400,
            node_type="PART",
            label=["400"],
            title="Part 400",
            children=[
                {
                    "node_type": "SUBPART",
                    "label": ["A"],
                    "title": "Subpart A",
                    "children": [
                        {
                            "node_type": "SUBJGRP",
                            "label": ["ECFRfoo"],
                            "title": "Group",
                            "children": [{"node_type": "SECTION", "label": ["400", "2"], "title": "Sec", "children": []}],
                        }
                    ],
                    "metadata": "drop",
                }
            ],
        )

        normalized = _module.normalize_part_for_eregs(part)
        subpart = normalized["children"][0]
        subject_group = subpart["children"][0]

        self.assertEqual(set(subpart.keys()), {"node_type", "label", "title", "children"})
        self.assertEqual(set(subject_group.keys()), {"node_type", "label", "title", "children"})


if __name__ == "__main__":
    unittest.main()
