import unittest
from importlib import util
from pathlib import Path
import sys
import types
from unittest.mock import patch


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
                "node_type": "SECTION",
                "label": ["433", "11"],
                "children": [
                    {"node_type": "Paragraph", "text": "(a) alpha"},
                    {"node_type": "Paragraph", "text": "(1) numeric"},
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

    def test_apply_paragraph_citations_builds_hierarchy_and_hash_fallback(self):
        part_children = [
            {
                "node_type": "SECTION",
                "label": ["433", "11"],
                "children": [
                    {"node_type": "Paragraph", "text": "(a) alpha", "marker": ["a"]},
                    {"node_type": "Paragraph", "text": "(1) numeric", "marker": ["1"]},
                    {"node_type": "Paragraph", "text": "plain paragraph", "marker": []},
                ],
            }
        ]

        _module._apply_paragraph_citations(types.SimpleNamespace(children=part_children))

        section_children = part_children[0]["children"]
        self.assertEqual(section_children[0]["label"], ["433", "11", "a"])
        self.assertEqual(section_children[1]["label"], ["433", "11", "a", "1"])
        self.assertEqual(len(section_children[2]["label"]), 3)
        self.assertRegex(section_children[2]["label"][2], r"^[0-9a-f]{32}$")

    def test_generate_paragraph_citation_legacy_case_matrix(self):
        cases = [
            {
                "name": "test-1-level",
                "marker": ["a", "1"],
                "prev": None,
                "expected": ["a", "1"],
                "has_error": False,
            },
            {
                "name": "test-2-levels",
                "marker": ["2"],
                "prev": ["a", "1"],
                "expected": ["a", "2"],
                "has_error": False,
            },
            {
                "name": "test-3-levels",
                "marker": ["iii"],
                "prev": ["b", "1", "ii"],
                "expected": ["b", "1", "iii"],
                "has_error": False,
            },
            {
                "name": "test-4-levels",
                "marker": ["B"],
                "prev": ["e", "3", "iii", "A"],
                "expected": ["e", "3", "iii", "B"],
                "has_error": False,
            },
            {
                "name": "test-empty-previous-citation",
                "marker": ["viii", "1"],
                "prev": [],
                "expected": [],
                "has_error": False,
            },
            {
                "name": "test-zero-length-marker",
                "marker": [],
                "prev": None,
                "expected": [],
                "has_error": False,
            },
            {
                "name": "test-letter-vs-roman",
                "marker": ["i", "1"],
                "prev": ["h", "3"],
                "expected": ["i", "1"],
                "has_error": False,
            },
            {
                "name": "test-letter-vs-roman-i",
                "marker": ["i"],
                "prev": ["h"],
                "expected": ["i"],
                "has_error": False,
            },
            {
                "name": "test-letter-vs-roman-v-1",
                "marker": ["v"],
                "prev": ["u"],
                "expected": ["v"],
                "has_error": False,
            },
            {
                "name": "test-letter-vs-roman-v-2",
                "marker": ["v"],
                "prev": ["u", "v", "w"],
                "expected": ["v"],
                "has_error": False,
            },
            {
                "name": "test-wrong-paragraph-order",
                "marker": ["iv"],
                "prev": ["b"],
                "expected": [],
                "has_error": True,
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                label, error = _module._generate_paragraph_citation(case["marker"], case["prev"])
                self.assertEqual(label, case["expected"])
                if case["has_error"]:
                    self.assertEqual(error, "this paragraph and its neighbor are not in the right order")
                else:
                    self.assertIsNone(error)

    def test_extract_marker_legacy_case_matrix(self):
        cases = [
            {"input": "(a)", "expected": ["a"]},
            {"input": "(6)(i)", "expected": ["6", "i"]},
            {"input": "(6)(i)(1)", "expected": ["6", "i", "1"]},
            {
                "input": "(2) <I>One of the following documents that show a U.S. place of birth and was created at least 5 years before the application for Medicaid.</I> (For children under 16 the document must have been created near the time of birth or 5 years before the date of application.) This document must be one of the following and show a U.S. place of birth",
                "expected": ["2"],
            },
            {
                "input": "(b) <I>Activities and rates.</I> (1) [Reserved]",
                "expected": ["b", "1"],
            },
            {
                "input": "(b)<I>Activities and rates.</I>(1)(i) [Reserved]",
                "expected": ["b", "1", "i"],
            },
            {
                "input": "(b)<I>Activities and rates.</I> -(1) [Reserved]",
                "expected": ["b", "1"],
            },
            {
                "input": "(b) <I>Activities and rates.</I> - (1) [Reserved]",
                "expected": ["b", "1"],
            },
            {
                "input": "(b) <I>Activities and rates.</I>-(1) [Reserved]",
                "expected": ["b", "1"],
            },
            {
                "input": "(c) <I>Filing requirements</I> - (1) <I>Authority to file.</I> - (i) A",
                "expected": ["c", "1", "i"],
            },
            {
                "input": "(3) <I>Publication of national limits.</I> If CMS determines under this paragraph (h)",
                "expected": ["3"],
            },
            {
                "input": "(<I>1</I>) A copy of the disallowance letter.",
                "expected": ["<I>1</I>"],
            },
            {
                "input": "(<I>ix</I>) A copy of the disallowance letter.",
                "expected": ["<I>ix</I>"],
            },
            {"input": "nothing", "expected": None},
        ]

        for case in cases:
            with self.subTest(text=case["input"]):
                self.assertEqual(_module._extract_marker(case["input"]), case["expected"])

    def test_apply_paragraph_citations_logs_wrong_order_and_keeps_previous_context(self):
        part_children = [
            {
                "node_type": "SECTION",
                "label": ["433", "11"],
                "children": [
                    {"node_type": "Paragraph", "text": "(b) top", "marker": ["b"]},
                    {"node_type": "Paragraph", "text": "(iv) wrong order", "marker": ["iv"]},
                    {"node_type": "Paragraph", "text": "(1) follows", "marker": ["1"]},
                ],
            }
        ]

        with self.assertLogs(_module.__name__, level="WARNING") as logs:
            _module._apply_paragraph_citations(types.SimpleNamespace(children=part_children))

        self.assertIn("Error generating paragraph citation", logs.output[0])

        section_children = part_children[0]["children"]
        self.assertEqual(section_children[0]["label"], ["433", "11", "b"])
        self.assertEqual(len(section_children[1]["label"]), 3)
        self.assertRegex(section_children[1]["label"][2], r"^[0-9a-f]{32}$")
        self.assertEqual(section_children[2]["label"], ["433", "11", "b", "1"])

    def test_apply_paragraph_citations_no_parent_case_hashes_without_warning(self):
        part_children = [
            {
                "node_type": "SECTION",
                "label": ["433", "11"],
                "children": [
                    {"node_type": "Paragraph", "text": "plain paragraph", "marker": []},
                    {"node_type": "Paragraph", "text": "(iv) no parent", "marker": ["iv"]},
                ],
            }
        ]

        with patch.object(_module.logger, "warning") as mock_warning:
            _module._apply_paragraph_citations(types.SimpleNamespace(children=part_children))

        mock_warning.assert_not_called()
        section_children = part_children[0]["children"]
        self.assertEqual(len(section_children[0]["label"]), 3)
        self.assertRegex(section_children[0]["label"][2], r"^[0-9a-f]{32}$")
        self.assertEqual(len(section_children[1]["label"]), 3)
        self.assertRegex(section_children[1]["label"][2], r"^[0-9a-f]{32}$")

    def test_rewrite_graphics_source_invalid_filename(self):
        self.assertIsNone(_module._rewrite_graphics_source("/graphics/NOEXT"))

    def test_rewrite_embedded_image_sources_updates_nodes_recursively(self):
        part_children = [
            {
                "node_type": "SECTION",
                "children": [
                    {"node_type": "Image", "src": "/graphics/ER18OC21.004.gif"},
                    {
                        "node_type": "Division",
                        "children": [
                            {"node_type": "Image", "src": "/graphics/ER18OC21.004.eps.gif"},
                            {"node_type": "Image", "src": "https://example.com/a.png"},
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
