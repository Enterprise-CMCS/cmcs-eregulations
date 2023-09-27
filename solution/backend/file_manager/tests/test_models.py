import pytest

from file_manager.models import UploadedFile


@pytest.mark.django_db
def test_extension():
    UploadedFile.objects.update_or_create(document_id="valid", file_name="C://valid.xls",)
    good_file = UploadedFile.objects.get(document_id="valid")
    print(good_file.__dict__)
    assert good_file.extension() == ".xls"


@pytest.mark.django_db
def test_key():
    UploadedFile.objects.update_or_create(document_id="valid", file_name="valid.doc",)
    good_file = UploadedFile.objects.get(document_id="valid")
    assert good_file.get_key() == 'uploaded_files/' + str(good_file.uid) + ".doc"
    UploadedFile.objects.update_or_create(document_id="no-extension", file_name="failure")
    bad_file = UploadedFile.objects.get(document_id="no-extension")
    with pytest.raises(ValueError):
        bad_file.get_key()
