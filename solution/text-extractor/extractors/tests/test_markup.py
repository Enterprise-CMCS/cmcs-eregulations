from . import FixtureTestCase


class TestMarkupExtractor(FixtureTestCase):
    def test_extract_html(self):
        self._test_file_type("html")

    def test_extract_low_confidence_html(self):
        self._test_file_type("html", variation="low-confidence")

    def test_extract_uscode_house_gov(self):
        self._test_file_type(
            "html",
            variation="uscode.house.gov",
            config={
                "backend": "web",
                "uri": "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396w-5",
            },
        )

    def test_extract_gao_gov(self):
        self._test_file_type(
            "html",
            variation="gao.gov",
            config={
                "backend": "web",
                "uri": "https://gao.gov/products/GAO-21-123",
            },
        )

    def test_extract_cmsgov_github_io(self):
        self._test_file_type(
            "html",
            variation="cmsgov.github.io",
            config={
                "backend": "web",
                "uri": "https://cmsgov.github.io/CMCS-DSG-DSS-Certification/",
            },
        )

    def test_extract_cms_gov(self):
        self._test_file_type(
            "html",
            variation="cms.gov",
            config={
                "backend": "web",
                "uri": "https://www.cms.gov/marketplace/resources/data/essential-health-benefits",
            },
        )

    def test_content_in_main_tag(self):
        self._test_file_type("html", variation="main_tag_test")

    def test_content_in_article_or_section_tags(self):
        self._test_file_type("html", variation="article_section_tag_test")

    def test_extract_htm(self):
        self._test_file_type("htm")

    def test_extract_xhtml(self):
        self._test_file_type("xhtml")

    def test_extract_xml(self):
        self._test_file_type("xml")
