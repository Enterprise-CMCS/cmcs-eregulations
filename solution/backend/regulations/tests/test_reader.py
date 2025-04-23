
import pytest
from django.http import Http404

from ..views.reader import AppendixReaderView, PartReaderView, SubpartReaderView


@pytest.fixture
def mock_context_subpart():
    return {
        "title": "42",
        "part": "400",
        "subpart": "A",
    }


@pytest.fixture
def mock_context_appendix_type_1():
    return {
        "title": "42",
        "part": "400",
        "appendix": ["APPENDIX", "VIII", "TO", "PART", "400"],
    }


@pytest.fixture
def mock_context_appendix_type_2():
    return {
        "title": "42",
        "part": "400",
        "appendix": ["APPENDIX", "TO", "PART", "400"],
    }


@pytest.fixture
def mock_context_appendix_invalid():
    return {
        "title": "42",
        "part": "400",
        "appendix": ["APPENDIX", "VIII"],
    }


@pytest.fixture
def mock_document():
    return {
        "children": [
            {"type": "subpart", "content": "Subpart A Content"},
            {"type": "appendix", "content": "Appendix VIII Content"},
            {"type": "appendix", "content": "Appendix to Part 400 Content"},
        ]
    }


@pytest.fixture
def mock_toc():
    return {
        "children": [
            {"type": "subpart", "identifier": ["A"]},
            {"type": "appendix", "identifier": ["APPENDIX", "VIII", "TO", "PART", "400"]},
            {"type": "appendix", "identifier": ["APPENDIX", "TO", "PART", "400"]},
        ]
    }


def test_part_reader_view_get_content(mock_context_subpart, mock_document):
    view = PartReaderView()
    content = view.get_content(mock_context_subpart, mock_document, None)
    assert content == mock_document


def test_subpart_reader_view_get_content(mock_context_subpart, mock_document, mock_toc):
    view = SubpartReaderView()
    content = view.get_content(mock_context_subpart, mock_document, mock_toc)
    assert content == mock_document["children"][0]


def test_appendix_reader_view_get_content(mock_context_appendix_type_1, mock_document, mock_toc):
    view = AppendixReaderView()
    content = view.get_content(mock_context_appendix_type_1, mock_document, mock_toc)
    assert content == mock_document["children"][1]


def test_appendix_reader_view_get_content_type_1(mock_context_appendix_type_1, mock_document, mock_toc):
    view = AppendixReaderView()
    content = view.get_content(mock_context_appendix_type_1, mock_document, mock_toc)
    assert content == mock_document["children"][1]


def test_appendix_reader_view_get_content_type_2(mock_context_appendix_type_2, mock_document, mock_toc):
    view = AppendixReaderView()
    content = view.get_content(mock_context_appendix_type_2, mock_document, mock_toc)
    assert content == mock_document["children"][2]


def test_appendix_reader_view_get_content_invalid(mock_context_appendix_invalid, mock_document, mock_toc):
    view = AppendixReaderView()
    with pytest.raises(Http404):
        view.get_content(mock_context_appendix_invalid, mock_document, mock_toc)
