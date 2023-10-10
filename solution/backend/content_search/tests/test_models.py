import pytest

from content_search.models import ContentIndex, establish_content_type
from file_manager.models import UploadedFile
from resources.models import FederalRegisterDocument, SupplementalContent


def add_supplemental_content():
    return SupplementalContent.objects.get_or_create(name="valid", url="valid.doc",)


def add_internal_document():
    return UploadedFile.objects.get_or_create(document_name='test', file_name='test')


def add_fr_doc():
    return FederalRegisterDocument.objects.get_or_create(name="valid", url="valid.doc",)


@pytest.mark.django_db
def test_index_created():
    total_index = ContentIndex.objects.all()
    assert total_index.count() == 0
    sc, created = add_supplemental_content()
    assert total_index.count() == 1
    id, created = add_internal_document()
    assert total_index.count() == 2
    fr, created = add_fr_doc()
    assert total_index.count() == 3
    sc.delete()
    id.delete()
    fr.delete()


@pytest.mark.django_db
def test_index_update():
    si, created = add_supplemental_content()
    file_index = ContentIndex.objects.get(supplemental_content=si)
    assert file_index.content == ''
    file_index.content = 'content is here'
    file_index.save()
    si.name = 'updated'
    si.save()
    file_index = ContentIndex.objects.get(supplemental_content=si)
    print(file_index.__dict__)
    assert file_index.doc_name_string == 'updated'
    assert file_index.content == 'content is here'
    si.delete()


@pytest.mark.django_db
def test_content_type():
    sc, created = add_supplemental_content()
    internal_doc, created = add_internal_document()
    fr, created = add_fr_doc()
    assert ContentIndex.objects.get(supplemental_content=sc).resource_type == 'external'
    assert ContentIndex.objects.get(fr_doc=fr).resource_type == 'external'
    assert ContentIndex.objects.get(file=internal_doc).resource_type == 'internal'
    none_type = establish_content_type(int)
    assert none_type is None
    sc.delete()
    fr.delete()
    internal_doc.delete()
