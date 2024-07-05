import pytest

from common.filters import IndexPopulatedFilter
from content_search.models import ContentIndex
from resources.models.internal_resources import InternalFile


@pytest.mark.django_db
def test_index_populated_filter():
    a = InternalFile.objects.create(document_id="a")
    b = InternalFile.objects.create(document_id="b")

    # Retrieve the existing ContentIndex instances linked to InternalFile instances
    index_a, created_a = ContentIndex.objects.get_or_create(resource=a)
    index_b, created_b = ContentIndex.objects.get_or_create(resource=b)

    # Update the content field for index_a
    index_a.content = "Hello world"
    index_a.save()

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
