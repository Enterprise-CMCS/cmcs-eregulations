import unittest
from importlib import util
from pathlib import Path
import sys
import types


def _load_module():
    worker_dir = Path(__file__).resolve().parent.parent / "ecfr-worker"
    module_path = worker_dir / "xml_parser" / "postprocess.py"

    package_name = "ecfr_worker_xml_postprocess_pkg"
    package = types.ModuleType(package_name)
    package.__path__ = [str(worker_dir)]
    sys.modules[package_name] = package

    xml_parser_package = types.ModuleType(f"{package_name}.xml_parser")
    xml_parser_package.__path__ = [str(worker_dir / "xml_parser")]
    sys.modules[f"{package_name}.xml_parser"] = xml_parser_package

    spec = util.spec_from_file_location(f"{package_name}.xml_parser.postprocess", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ecfr worker xml_parser.postprocess module")

    module = util.module_from_spec(spec)
    sys.modules[f"{package_name}.xml_parser.postprocess"] = module
    spec.loader.exec_module(module)
    return module


_module = _load_module()


class EcfrWorkerXmlPostprocessTests(unittest.TestCase):
    def test_postprocess_runs_markers_before_citations(self):
        part_children = [
            {
                "node_type": "section",
                "label": ["433", "11"],
                "children": [
                    {"node_type": "paragraph", "text": "(a) alpha"},
                    {"node_type": "paragraph", "text": "(1) numeric"},
                ],
            }
        ]

        part = types.SimpleNamespace(children=part_children)
        _module.postprocess_part_node(part)

        section_children = part_children[0]["children"]
        self.assertEqual(section_children[0]["marker"], ["a"])
        self.assertEqual(section_children[0]["label"], ["433", "11", "a"])
        self.assertEqual(section_children[1]["marker"], ["1"])
        self.assertEqual(section_children[1]["label"], ["433", "11", "a", "1"])

    def test_apply_paragraph_markers_extracts_leading_markers(self):
        part = {
            "children": [
                {
                    "node_type": "section",
                    "label": ["433", "11"],
                    "children": [
                        {"node_type": "paragraph", "text": "(a) first"},
                        {"node_type": "paragraph", "text": "(1) second"},
                    ],
                }
            ]
        }

        _module._apply_paragraph_markers(types.SimpleNamespace(children=part["children"]))

        section = part["children"][0]
        self.assertEqual(section["children"][0]["marker"], ["a"])
        self.assertEqual(section["children"][1]["marker"], ["1"])

    def test_apply_paragraph_citations_builds_hierarchy_and_hash_fallback(self):
        part_children = [
            {
                "node_type": "section",
                "label": ["433", "11"],
                "children": [
                    {"node_type": "paragraph", "text": "(a) alpha", "marker": ["a"]},
                    {"node_type": "paragraph", "text": "(1) numeric", "marker": ["1"]},
                    {"node_type": "paragraph", "text": "plain paragraph", "marker": []},
                ],
            }
        ]

        _module._apply_paragraph_citations(types.SimpleNamespace(children=part_children))

        section_children = part_children[0]["children"]
        self.assertEqual(section_children[0]["label"], ["433", "11", "a"])
        self.assertEqual(section_children[1]["label"], ["433", "11", "a", "1"])
        self.assertEqual(len(section_children[2]["label"]), 3)
        self.assertRegex(section_children[2]["label"][2], r"^[0-9a-f]{32}$")

    def test_generate_paragraph_citation_handles_roman_edge_cases(self):
        # i at level 2 with no level-1 predecessor should start fresh.
        self.assertEqual(_module._generate_paragraph_citation(["i"], ["a", "2", "c"]), ["i"])

        # v should reset when previous third token is not iv.
        self.assertEqual(_module._generate_paragraph_citation(["v"], ["a", "2", "iii"]), ["v"])

    def test_rewrite_graphics_source_normal_file(self):
        rewritten = _module._rewrite_graphics_source("/graphics/ER18OC21.004.gif")
        self.assertEqual(rewritten, "https://images.federalregister.gov/ER18OC21.004/large.png")

    def test_rewrite_graphics_source_eps_file(self):
        rewritten = _module._rewrite_graphics_source("/graphics/ER18OC21.004.eps.gif")
        self.assertEqual(rewritten, "https://images.federalregister.gov/ER18OC21.004/large.png")

    def test_rewrite_graphics_source_invalid_filename(self):
        self.assertIsNone(_module._rewrite_graphics_source("/graphics/NOEXT"))

    def test_rewrite_embedded_image_sources_updates_nodes_recursively(self):
        part_children = [
            {
                "node_type": "section",
                "children": [
                    {"node_type": "image", "src": "/graphics/ER18OC21.004.gif"},
                    {
                        "node_type": "division",
                        "children": [
                            {"node_type": "image", "src": "/graphics/ER18OC21.004.eps.gif"},
                            {"node_type": "image", "src": "https://example.com/a.png"},
                        ],
                    },
                ],
            }
        ]

        _module._rewrite_embedded_image_sources(types.SimpleNamespace(children=part_children))

        section = part_children[0]
        self.assertEqual(
            section["children"][0]["src"],
            "https://images.federalregister.gov/ER18OC21.004/large.png",
        )
        self.assertEqual(
            section["children"][1]["children"][0]["src"],
            "https://images.federalregister.gov/ER18OC21.004/large.png",
        )
        self.assertEqual(section["children"][1]["children"][1]["src"], "https://example.com/a.png")


if __name__ == "__main__":
    unittest.main()
