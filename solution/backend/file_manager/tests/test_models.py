import pytest

from file_manager.models import UploadedFile


@pytest.mark.django_db
def test_key():
    UploadedFile.objects.update_or_create(name="valid", file_name="valid.doc",)
    good_file = UploadedFile.objects.get(name="valid")
    assert good_file.get_key() == 'uploaded_files/' + str(good_file.uid) + ".doc"
    UploadedFile.objects.update_or_create(name="no-extension", file_name="failure")
    bad_file = UploadedFile.objects.get(name="no-extension")
    with pytest.raises(ValueError):
        bad_file.get_key()
