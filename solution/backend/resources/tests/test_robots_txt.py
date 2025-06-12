import pytest
from backend.resources.aws_utils import _should_ignore_robots_txt

@pytest.mark.parametrize(
    "url,allow_list,expected",
    [
        # No allow_list, should not ignore any
        ("https://example.com", [], False),
        ("http://sub.example.com/page", [], False),
        # Allow list with domain only
        ("https://example.com", ["example.com"], True),
        ("https://other.com", ["example.com"], False),
        # Allow list with subdomain
        ("https://sub.example.com", ["sub.example.com"], True),
        ("https://sub.example.com", ["example.com"], False),
        # Allow list with path
        ("https://example.com/page.html", ["example.com"], True),
        ("https://other.com/page.html", ["example.com"], False),
        ("https://sub.example.com/page.html", ["example.com"], True),
        # Mixed allow_list
        ("https://foo.example.com", ["example.com", "https://abc.com/path.txt"], True),
        ("https://bar.other.com", ["example.com", "https://abc.com/path.txt"], False),
    ]
)
def test_should_ignore_robots_txt(url, allow_list, expected):
    assert _should_ignore_robots_txt(url, allow_list) == expected
