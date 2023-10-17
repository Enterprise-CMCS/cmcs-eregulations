import pytest

from content_search.functions import add_to_index
from content_search.models import ContentIndex
from file_manager.models import UploadedFile
from resources.models import FederalRegisterDocument, SupplementalContent


def add_supplemental_content():
    sup, _ = SupplementalContent.objects.get_or_create(name="valid", url="valid.doc",)
    add_to_index(sup)
    return sup


def add_internal_document():
    up, _ = UploadedFile.objects.get_or_create(document_name='test', file_name='test')
    add_to_index(up)
    return up


def add_fr_doc():
    fr_doc, _ = FederalRegisterDocument.objects.get_or_create(name="valid", url="valid.doc",)
    add_to_index(fr_doc)
    return fr_doc


def clean_up():
    SupplementalContent.objects.all().delete()
    FederalRegisterDocument.objects.all().delete()
    UploadedFile.objects.all().delete()
    ContentIndex.objects.all().delete()


@pytest.mark.django_db
def test_index_created():
    total_index = ContentIndex.objects.all()
    assert total_index.count() == 0
    add_supplemental_content()
    assert total_index.count() == 1
    add_internal_document()
    assert total_index.count() == 2
    add_fr_doc()
    assert total_index.count() == 3
    clean_up()


@pytest.mark.django_db
def test_index_update():
    si = add_supplemental_content()
    fr = add_fr_doc()
    up = add_internal_document()
    file_index = ContentIndex.objects.get(supplemental_content=si)
    assert file_index.content is None
    file_index.content = 'content is here'
    file_index.save()
    si.name = 'updated'
    si.save()
    add_to_index(si)
    file_index = ContentIndex.objects.get(supplemental_content=si)
    assert file_index.doc_name_string == 'updated'
    assert file_index.content == 'content is here'

    file_index = ContentIndex.objects.get(fr_doc=fr)
    assert file_index.content is None
    file_index.content = 'content is here'
    file_index.save()
    fr.name = 'updated'
    fr.save()
    add_to_index(fr)
    file_index = ContentIndex.objects.get(fr_doc=fr)
    assert file_index.doc_name_string == 'updated'
    assert file_index.content == 'content is here'

    file_index = ContentIndex.objects.get(file=up)
    assert file_index.content is None
    file_index.content = 'content is here'
    file_index.save()
    up.document_name = 'updated'
    up.save()
    add_to_index(up)
    file_index = ContentIndex.objects.get(file=up)
    assert file_index.doc_name_string == 'updated'
    assert file_index.content == 'content is here'
    clean_up()


@pytest.mark.django_db
def test_content_type():
    sc = add_supplemental_content()
    internal_doc = add_internal_document()
    fr = add_fr_doc()
    assert ContentIndex.objects.get(supplemental_content=sc).resource_type == 'external'
    assert ContentIndex.objects.get(fr_doc=fr).resource_type == 'external'
    assert ContentIndex.objects.get(file=internal_doc).resource_type == 'internal'
    clean_up()
