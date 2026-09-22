import unittest
import json
from importlib import util
from pathlib import Path
import sys
import types


def _load_module():
    worker_dir = Path(__file__).resolve().parent.parent / "ecfr-worker"
    module_path = worker_dir / "xml_parser" / "__init__.py"

    package_name = "ecfr_worker_xml_pkg"
    package = types.ModuleType(package_name)
    package.__path__ = [str(worker_dir)]
    sys.modules[package_name] = package

    spec = util.spec_from_file_location(
        f"{package_name}.xml_parser",
        module_path,
        submodule_search_locations=[str(worker_dir / "xml_parser")],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ecfr worker xml_parser module")

    module = util.module_from_spec(spec)
    sys.modules[f"{package_name}.xml_parser"] = module
    spec.loader.exec_module(module)
    return module


_module = _load_module()
_fixtures_dir = Path(__file__).resolve().parent / "fixtures"


class EcfrWorkerXmlParserTests(unittest.TestCase):
    def test_parse_part_xml_to_document_returns_dict_for_minimal_part(self):
        xml = """
<DIV5 TYPE="PART" N="400">
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
  <DIV8 TYPE="SECTION" N="400.1">
    <HEAD>Sec. 400.1 Test Section</HEAD>
    <P>(a) <I>Test paragraph text.</I> (1) Nested paragraph text.</P>
  </DIV8>
</DIV5>
""".strip()

        document = _module.parse_part_xml_to_document(xml, title_number=42, part_number=400)
        expected = json.loads((_fixtures_dir / "ecfr_xml_minimal_expected_document.json").read_text(encoding="utf-8"))

        self.assertIsInstance(document, dict)
        self.assertEqual(document, expected)

    def test_parse_part_xml_to_document_rejects_malformed_xml(self):
        with self.assertRaises(_module.EcfrXmlParseError):
            _module.parse_part_xml_to_document("<DIV5><HEAD>broken", title_number=42, part_number=400)


if __name__ == "__main__":
    unittest.main()
