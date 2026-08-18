import unittest
from importlib import util
from pathlib import Path
import sys
import types


def _load_models_module():
    worker_dir = Path(__file__).resolve().parent.parent / "ecfr-worker"
    module_path = worker_dir / "xml_parser" / "models.py"

    package_name = "ecfr_worker_xml_models_pkg"
    package = types.ModuleType(package_name)
    package.__path__ = [str(worker_dir)]
    sys.modules[package_name] = package

    xml_parser_package = types.ModuleType(f"{package_name}.xml_parser")
    xml_parser_package.__path__ = [str(worker_dir / "xml_parser")]
    sys.modules[f"{package_name}.xml_parser"] = xml_parser_package

    spec = util.spec_from_file_location(f"{package_name}.xml_parser.models", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ecfr worker xml_parser.models module")

    module = util.module_from_spec(spec)
    sys.modules[f"{package_name}.xml_parser.models"] = module
    spec.loader.exec_module(module)
    return module


_module = _load_models_module()
PartNode = _module.PartNode


class EcfrWorkerXmlModelsTests(unittest.TestCase):
    def test_part_node_accepts_valid_values(self):
        part = PartNode(
            title_number=42,
            part_number=400,
            node_type="PART",
            label=["400"],
            title="Part 400",
        )

        self.assertEqual(part.title_number, 42)
        self.assertEqual(part.part_number, 400)
        self.assertEqual(part.node_type, "PART")
        self.assertEqual(part.label, ["400"])

    def test_part_node_rejects_non_positive_title_number(self):
        with self.assertRaisesRegex(ValueError, "title_number must be a positive integer"):
            PartNode(title_number=0, part_number=400)

    def test_part_node_rejects_non_positive_part_number(self):
        with self.assertRaisesRegex(ValueError, "part_number must be a positive integer"):
            PartNode(title_number=42, part_number=-1)

    def test_part_node_rejects_non_part_node_type(self):
        with self.assertRaisesRegex(ValueError, 'node_type must be exactly "PART"'):
            PartNode(title_number=42, part_number=400, node_type="SECTION")

    def test_part_node_rejects_non_string_labels(self):
        with self.assertRaisesRegex(ValueError, "label must be a list of strings"):
            PartNode(title_number=42, part_number=400, label=["400", 1])


if __name__ == "__main__":
    unittest.main()
