import pytest

from resources.utils.aws_utils import _should_ignore_robots_txt


@pytest.mark.parametrize(
    "url,extract_url,allow_list,expected",
    [
        # No allow_list, should not ignore any
        ("https://example.com", "", [], False),
        ("http://sub.example.com/page", "", [], False),
        # Allow list with domain only
        ("https://example.com", "", ["example.com"], True),
        ("https://other.com", "", ["example.com"], False),
        # Allow list with subdomain
        ("https://sub.example.com", "", ["sub.example.com"], True),
        ("https://sub.example.com", "", ["example.com"], True),
        # Allow list with path
        ("https://example.com/page.html", "", ["example.com"], True),
        ("https://other.com/page.html", "", ["example.com"], False),
        ("https://sub.example.com/page.html", "", ["example.com"], True),
        # Mixed allow_list
        ("https://foo.example.com", "", ["example.com", "https://abc.com/path.txt"], True),
        ("https://bar.other.com", "", ["example.com", "https://abc.com/path.txt"], False),
        # extract_url should be used if available
        ("https://unindexablepage.com", "https://example.com/something", ["example.com"], True),
    ]
)
def test_should_ignore_robots_txt(url, extract_url, allow_list, expected):
    def resource():
        return None
    resource.url = url
    resource.extract_url = extract_url

    assert _should_ignore_robots_txt(resource, allow_list) == expected
