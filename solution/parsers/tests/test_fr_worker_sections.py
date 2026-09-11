import unittest
from importlib import util
from pathlib import Path
from unittest.mock import Mock, patch

import requests


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "fr-worker" / "fedreg_client.py"
    spec = util.spec_from_file_location("fr_worker_fedreg_client", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load fr worker fedreg_client module")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load_module()


class FetchFullTextSectionsTests(unittest.TestCase):
    def _response(self, xml):
        response = Mock()
        response.raise_for_status.return_value = None
        response.content = xml.encode("utf-8")
        return response

    def test_valid_sections(self):
        xml = """
            <PRORULE>
                <PREAMB>
                    <SUBAGY>Centers for Medicare &amp; Medicaid Services</SUBAGY>
                    <CFR>42 CFR Parts 438, 440, 457, and 460</CFR>
                    <CFR>45 CFR Parts 41.</CFR>
                    <CFR>47 CFR Parts 123</CFR>
                </PREAMB>
                <TEST>Some data</TEST>
                <SUPLINF>
                    <SECTION><SECTNO>§\u2009438.502 </SECTNO><SUBJECT>Definitions.</SUBJECT></SECTION>
                    <SECTION><SECTNO>§\u200941.118 </SECTNO><SUBJECT>abc xyz...</SUBJECT></SECTION>
                    <SECTION><SECTNO>§\u2009123.1418 </SECTNO><SUBJECT>abc xyz asdfasdf...</SUBJECT></SECTION>
                </SUPLINF>
            </PRORULE>
        """
        with patch.object(_module, "requests") as mock_requests:
            mock_requests.get.return_value = self._response(xml)
            sections, ranges, part_map = _module.fetch_full_text_sections("https://example/x.xml", {"42", "45"})

        self.assertEqual(sections, ["438.502", "41.118", "123.1418"])
        self.assertEqual(ranges, [])
        self.assertEqual(
            part_map,
            {"438": "42", "440": "42", "457": "42", "460": "42", "41": "45"},
        )

    def test_section_and_range_variants(self):
        cases = [
            (
                "single-range",
                """
                <SUPLINF>
                    <SECTION><SECTNO>§\u2009438.502-438.700 </SECTNO><SUBJECT>Definitions.</SUBJECT></SECTION>
                </SUPLINF>
                """,
                [],
                ["438.502-438.700"],
            ),
            (
                "mixed-sections-and-range",
                """
                <SUPLINF>
                    <SECTION><SECTNO>§\u2009438.502 </SECTNO></SECTION>
                    <SECTION><SECTNO>§\u200941.118 </SECTNO></SECTION>
                    <SECTION><SECTNO>§\u2009438.502-438.700 </SECTNO></SECTION>
                </SUPLINF>
                """,
                ["438.502", "41.118"],
                ["438.502-438.700"],
            ),
        ]

        for case_name, suplinf_body, expected_sections, expected_ranges in cases:
            with self.subTest(case=case_name):
                xml = f"""
                    <PRORULE>
                        <PREAMB>
                            <CFR>42 CFR Parts 438, 440, 457, and 460</CFR>
                            <CFR>45 CFR Parts 41.</CFR>
                            <CFR>47 CFR Parts 123</CFR>
                        </PREAMB>
                        {suplinf_body}
                    </PRORULE>
                """
                with patch.object(_module, "requests") as mock_requests:
                    mock_requests.get.return_value = self._response(xml)
                    sections, ranges, part_map = _module.fetch_full_text_sections("https://example/x.xml", {"42", "45"})

                self.assertEqual(sections, expected_sections)
                self.assertEqual(ranges, expected_ranges)
                self.assertEqual(part_map["438"], "42")

    def test_bad_xml_raises(self):
        xml = """
            PRORULE>
                <TEST>Some data</TEST>
                <SUPLINF>
                    <SECTION><SECTNO>\u00a7447.502 </SECTNO></SECTION>
                </SUPLINF>
            </PRORULE>
        """
        with patch.object(_module, "requests") as mock_requests:
            mock_requests.get.return_value = self._response(xml)
            with self.assertRaisesRegex(_module.FedRegClientError, "could not be parsed"):
                _module.fetch_full_text_sections("https://example/x.xml", {"42"})

    def test_http_error_raises(self):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError(response=Mock(status_code=500))
        with patch.object(_module, "requests") as mock_requests:
            mock_requests.get.return_value = response
            with self.assertRaisesRegex(_module.FedRegClientError, "full text request failed"):
                _module.fetch_full_text_sections("https://example/x.xml", {"42"})


class ExtractSectionTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(_module._extract_section("\u00a7 430.12"), ("430.12", ""))

    def test_invisible_space(self):
        self.assertEqual(_module._extract_section("\u00a7ㅤ430.11"), ("430.11", ""))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            _module._extract_section("\u00a7 430")

    def test_no_symbol(self):
        self.assertEqual(_module._extract_section("430.10"), ("430.10", ""))

    def test_ranges(self):
        self.assertEqual(_module._extract_section("430.10-430.20"), ("", "430.10-430.20"))


class ExtractCFRTests(unittest.TestCase):
    def test_multi_part(self):
        self.assertEqual(
            _module._extract_cfr("45 CFR Parts 80, 84, 86, 91, 92, 147, 155, and 156"),
            ("45", ["80", "84", "86", "91", "92", "147", "155", "156"]),
        )

    def test_single_part(self):
        self.assertEqual(_module._extract_cfr("42 CFR Part 438."), ("42", ["438"]))

    def test_no_parts(self):
        with self.assertRaises(ValueError):
            _module._extract_cfr("42 CFR Part")

    def test_empty_string(self):
        with self.assertRaises(ValueError):
            _module._extract_cfr("   ")

    def test_invalid_title(self):
        with self.assertRaises(ValueError):
            _module._extract_cfr("blah CFR Part 438.")

    def test_title_only(self):
        with self.assertRaises(ValueError):
            _module._extract_cfr("42")


if __name__ == "__main__":
    unittest.main()
