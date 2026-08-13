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

        self.assertEqual(part.node_type, "part")
        self.assertEqual(part.label, ["400"])
        self.assertEqual(part.title, "Part 400 - Test Part")
        self.assertEqual(part.authority, {"node_type": "authority", "header": "Authority:", "content": "42 U.S.C. 1302."})
        self.assertEqual(part.source, {"node_type": "source", "header": "Source:", "content": "90 FR 12345."})
        self.assertEqual(
            part.editorial_note,
            {"node_type": "editorial_note", "header": "Editorial Note:", "content": "Some note."},
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
        self.assertEqual(children[0]["node_type"], "subpart")
        self.assertEqual(children[1]["node_type"], "section")
        self.assertEqual(children[2]["node_type"], "appendix")

    def test_parse_section_child_maps_supported_tags(self):
        section_xml = """
<DIV8 N="400.1" TYPE="SECTION">
  <HEAD>Sec. 400.1</HEAD>
  <P>(a) Paragraph text.</P>
  <FP>Flush</FP>
  <img src="/graphics/abc.gif" />
  <EXTRACT>Extract content</EXTRACT>
  <CITA>Citation content</CITA>
  <SECAUTH>Sec auth</SECAUTH>
  <FTNT>Footnote</FTNT>
  <DIV>Division</DIV>
  <EFFDNOT><HED>Effective Date Note:</HED><PSPACE>Content</PSPACE></EFFDNOT>
</DIV8>
""".strip()
        root = _module._parse_xml_root(section_xml)
        parsed = _module._parse_section(root)

        self.assertEqual(parsed["node_type"], "section")
        child_types = [child["node_type"] for child in parsed["children"]]
        self.assertEqual(
            child_types,
            [
                "paragraph",
                "flush_paragraph",
                "image",
                "extract",
                "citation",
                "section_authority",
                "footnote",
                "division",
                "effective_date_note",
            ],
        )

    def test_parse_appendix_child_maps_supported_tags(self):
        appendix_xml = """
<DIV9 N="Appendix A to Part 400" TYPE="APPENDIX">
  <HEAD>Appendix A</HEAD>
  <P>Paragraph text.</P>
  <FP>Flush</FP>
  <HD1>Heading 1</HD1>
  <HD2>Heading 2</HD2>
  <HD3>Heading 3</HD3>
  <DIV>Division</DIV>
  <TABLE>Table content</TABLE>
  <FTNT>Footnote</FTNT>
  <CITA>Citation</CITA>
</DIV9>
""".strip()
        root = _module._parse_xml_root(appendix_xml)
        parsed = _module._parse_appendix(root)

        self.assertEqual(parsed["node_type"], "appendix")
        self.assertEqual(parsed["label"], ["Appendix", "A", "to", "Part", "400"])
        child_types = [child["node_type"] for child in parsed["children"]]
        self.assertEqual(
            child_types,
            [
                "paragraph",
                "flush_paragraph",
                "heading",
                "heading",
                "heading",
                "division",
                "table",
                "footnote",
                "citation",
            ],
        )


if __name__ == "__main__":
    unittest.main()
