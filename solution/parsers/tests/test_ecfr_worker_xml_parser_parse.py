import unittest
from importlib import util
from pathlib import Path
import sys
import types


def _load_module():
    worker_dir = Path(__file__).resolve().parent.parent / "ecfr-worker"
    module_path = worker_dir / "xml_parser" / "parse.py"

    package_name = "ecfr_worker_xml_parse_pkg"
    package = types.ModuleType(package_name)
    package.__path__ = [str(worker_dir)]
    sys.modules[package_name] = package

    xml_parser_package = types.ModuleType(f"{package_name}.xml_parser")
    xml_parser_package.__path__ = [str(worker_dir / "xml_parser")]
    sys.modules[f"{package_name}.xml_parser"] = xml_parser_package

    spec = util.spec_from_file_location(f"{package_name}.xml_parser.parse", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ecfr worker xml_parser.parse module")

    module = util.module_from_spec(spec)
    sys.modules[f"{package_name}.xml_parser.parse"] = module
    spec.loader.exec_module(module)
    return module


_module = _load_module()


class EcfrWorkerXmlParserParseTests(unittest.TestCase):
    def test_parse_part_root_maps_metadata_nodes(self):
        xml = """
<DIV5 N="400" TYPE="PART">
  <HEAD>Part 400 - Test Part</HEAD>
  <AUTH>
    <HED>Authority:</HED>
    <PSPACE>42 U.S.C. 1302.</PSPACE>
  </AUTH>
  <SOURCE>
    <HED>Source:</HED>
    <PSPACE>90 FR 12345.</PSPACE>
  </SOURCE>
  <EDNOTE>
    <HED>Editorial Note:</HED>
    <PSPACE>Some note.</PSPACE>
  </EDNOTE>
</DIV5>
""".strip()
        root = _module._parse_xml_root(xml)

        part = _module._parse_part_root(root, title_number=42, part_number=400)

        self.assertEqual(part.node_type, "PART")
        self.assertEqual(part.label, ["400"])
        self.assertEqual(part.title, "Part 400 - Test Part")
        self.assertEqual(part.authority, {"node_type": "Authority", "header": "Authority:", "content": "42 U.S.C. 1302."})
        self.assertEqual(part.source, {"node_type": "Source", "header": "Source:", "content": "90 FR 12345."})
        self.assertEqual(
            part.editorial_note,
            {"node_type": "EdNote", "header": "Editorial Note:", "content": "Some note."},
        )

    def test_parse_part_root_rejects_non_div5(self):
        root = _module._parse_xml_root("<DIV8 TYPE=\"SECTION\" N=\"400.1\"></DIV8>")
        with self.assertRaisesRegex(_module.EcfrXmlParseError, "expected part root tag DIV5"):
            _module._parse_part_root(root, title_number=42, part_number=400)

    def test_parse_part_root_rejects_non_part_type(self):
        root = _module._parse_xml_root("<DIV5 TYPE=\"SECTION\" N=\"400\"></DIV5>")
        with self.assertRaisesRegex(_module.EcfrXmlParseError, "expected part TYPE=PART"):
            _module._parse_part_root(root, title_number=42, part_number=400)

    def test_parse_part_children_dispatches_div6_div8_div9(self):
        xml = """
<DIV5 N="400" TYPE="PART">
  <DIV6 N="A" TYPE="SUBPART">
    <HEAD>Subpart A</HEAD>
  </DIV6>
  <DIV8 N="400.1" TYPE="SECTION">
    <HEAD>Sec. 400.1</HEAD>
    <P>(a) Para text.</P>
  </DIV8>
  <DIV9 N="Appendix A to Part 400" TYPE="APPENDIX">
    <HEAD>Appendix A</HEAD>
    <P>Appendix text.</P>
  </DIV9>
</DIV5>
""".strip()
        root = _module._parse_xml_root(xml)

        children = _module._parse_part_children(root)

        self.assertEqual(len(children), 3)
        self.assertEqual(children[0]["node_type"], "SUBPART")
        self.assertEqual(children[1]["node_type"], "SECTION")
        self.assertEqual(children[2]["node_type"], "APPENDIX")

    def test_parse_div_node_type_uses_type_attribute_then_fallback(self):
        with_type = _module._parse_xml_root('<DIV8 TYPE=" section " N="400.1"></DIV8>')
        without_type = _module._parse_xml_root('<DIV8 N="400.1"></DIV8>')

        self.assertEqual(_module._resolve_div_node_type(with_type), "SECTION")
        self.assertEqual(_module._resolve_div_node_type(without_type), "SECTION")

    def test_parse_subject_group_title_preserves_inner_xml(self):
        subject_group_xml = """
<DIV7 N="A" TYPE="SUBJGRP">
  <HEAD>General <I>Requirements</I></HEAD>
  <DIV8 N="400.1" TYPE="SECTION">
    <HEAD>Sec. 400.1</HEAD>
    <P>(a) Paragraph text.</P>
  </DIV8>
</DIV7>
""".strip()
        root = _module._parse_xml_root(subject_group_xml)

        parsed = _module._parse_subject_group(root)

        self.assertEqual(parsed["node_type"], "SUBJGRP")
        self.assertEqual(parsed["title"], "General <I>Requirements</I>")
        self.assertEqual(parsed["children"][0]["node_type"], "SECTION")

    def test_parse_subpart_parses_each_source_child_directly(self):
        subpart_xml = """
<DIV6 N="A" TYPE="SUBPART">
  <HEAD>Subpart A</HEAD>
  <SOURCE>
    <HED>Source:</HED>
    <PSPACE>90 FR 11111.</PSPACE>
  </SOURCE>
  <SOURCE>
    <HED>Source:</HED>
    <PSPACE>90 FR 22222.</PSPACE>
  </SOURCE>
</DIV6>
""".strip()
        root = _module._parse_xml_root(subpart_xml)

        parsed = _module._parse_subpart(root)
        source_children = [child for child in parsed["children"] if child.get("node_type") == "Source"]

        self.assertEqual(len(source_children), 2)
        self.assertEqual(source_children[0]["content"], "90 FR 11111.")
        self.assertEqual(source_children[1]["content"], "90 FR 22222.")

    def test_parse_section_child_maps_supported_tags(self):
        section_xml = """
<DIV8 N="400.1" TYPE="SECTION">
  <HEAD>Sec. 400.1</HEAD>
  <P>(a) <I>Paragraph</I> text.</P>
  <FP>Flush</FP>
  <img src="/graphics/abc.gif" />
  <EXTRACT><HD1>Extract heading</HD1></EXTRACT>
  <CITA><I>Citation</I> content</CITA>
  <SECAUTH>Sec <E T="03">auth</E></SECAUTH>
  <FTNT>Footnote</FTNT>
  <DIV><P>Division paragraph</P></DIV>
  <EFFDNOT><HED>Effective Date Note:</HED><PSPACE>Content</PSPACE></EFFDNOT>
</DIV8>
""".strip()
        root = _module._parse_xml_root(section_xml)
        parsed = _module._parse_section(root)

        self.assertEqual(parsed["node_type"], "SECTION")
        child_types = [child["node_type"] for child in parsed["children"]]
        self.assertEqual(
            child_types,
            [
                "Paragraph",
                "FlushParagraph",
                "Image",
                "Extract",
                "Citation",
                "SectionAuthority",
                "FootNote",
                "Division",
                "EffectiveDateNote",
            ],
        )
        self.assertIn("<I>Paragraph</I>", parsed["children"][0]["text"])
        self.assertIn("<HD1>Extract heading</HD1>", parsed["children"][3]["content"])
        self.assertIn("<I>Citation</I>", parsed["children"][4]["content"])
        self.assertIn("<E T=\"03\">auth</E>", parsed["children"][5]["content"])
        self.assertIn("<P>Division paragraph</P>", parsed["children"][7]["content"])

    def test_parse_section_splits_multi_marker_paragraph_nodes(self):
        section_xml = """
<DIV8 N="400.2" TYPE="SECTION">
  <HEAD>Sec. 400.2</HEAD>
  <P>(a) <I>Basis, purpose, and definitions.</I> (1) Nested marker text.</P>
</DIV8>
""".strip()
        root = _module._parse_xml_root(section_xml)

        parsed = _module._parse_section(root)

        self.assertEqual(len(parsed["children"]), 2)
        self.assertEqual(parsed["children"][0]["node_type"], "Paragraph")
        self.assertEqual(parsed["children"][1]["node_type"], "Paragraph")
        self.assertTrue(parsed["children"][0]["text"].lstrip().startswith("(a)"))
        self.assertIn("<I>Basis, purpose, and definitions.</I>", parsed["children"][0]["text"])
        self.assertTrue(parsed["children"][1]["text"].lstrip().startswith("(1)"))

    def test_parse_section_does_not_split_when_reserved_follows_next_marker(self):
        section_xml = """
<DIV8 N="400.3" TYPE="SECTION">
  <HEAD>Sec. 400.3</HEAD>
  <P>(b) Activities and rates. (1) [Reserved]</P>
</DIV8>
""".strip()
        root = _module._parse_xml_root(section_xml)

        parsed = _module._parse_section(root)

        self.assertEqual(len(parsed["children"]), 1)
        self.assertEqual(parsed["children"][0]["node_type"], "Paragraph")
        self.assertIn("(1) [Reserved]", parsed["children"][0]["text"])

    def test_parse_appendix_child_maps_supported_tags(self):
        appendix_xml = """
<DIV9 N="Appendix A to Part 400" TYPE="APPENDIX">
  <HEAD>Appendix A</HEAD>
  <P>Paragraph <I>text</I>.</P>
  <FP>Flush</FP>
  <HD1>Heading 1</HD1>
  <HD2>Heading 2</HD2>
  <HD3>Heading 3</HD3>
  <DIV><P>Division</P></DIV>
  <TABLE><TR><TD>Table content</TD></TR></TABLE>
  <FTNT>Footnote</FTNT>
  <CITA><I>Citation</I></CITA>
</DIV9>
""".strip()
        root = _module._parse_xml_root(appendix_xml)
        parsed = _module._parse_appendix(root)

        self.assertEqual(parsed["node_type"], "APPENDIX")
        self.assertEqual(parsed["label"], ["Appendix", "A", "to", "Part", "400"])
        child_types = [child["node_type"] for child in parsed["children"]]
        self.assertEqual(
            child_types,
            [
                "Paragraph",
                "FlushParagraph",
                "Heading",
                "Heading2",
                "Heading3",
                "Division",
                "Table",
                "FootNote",
                "Citation",
            ],
        )
        self.assertIn("<I>text</I>", parsed["children"][0]["text"])
        self.assertIn("<P>Division</P>", parsed["children"][5]["content"])
        self.assertIn("<TR><TD>Table content</TD></TR>", parsed["children"][6]["content"])
        self.assertIn("<I>Citation</I>", parsed["children"][8]["content"])


if __name__ == "__main__":
    unittest.main()
