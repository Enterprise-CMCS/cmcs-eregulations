import pytest

from common.filters import IndexPopulatedFilter
from content_search.models import ContentIndex
from resources.models.internal_resources import InternalFile


@pytest.mark.django_db
def test_index_populated_filter():
    a = InternalFile.objects.create(document_name="a")
    b = InternalFile.objects.create(document_name="b")
    ContentIndex.objects.create(file=a, content="Hello world")
    ContentIndex.objects.create(file=b)

    # Test when populated filter is not set
    results = IndexPopulatedFilter(None, {}, None, None).queryset(None, InternalFile.objects.all())
    assert a in results
    assert b in results

    # Test when populated filter is set to "yes"
    results = IndexPopulatedFilter(None, {"populated": ["yes"]}, None, None).queryset(None, InternalFile.objects.all())
    assert a in results
    assert b not in results

    # Test when populated filter is set to "no"
    results = IndexPopulatedFilter(None, {"populated": ["no"]}, None, None).queryset(None, InternalFile.objects.all())
    assert a not in results
    assert b in results
