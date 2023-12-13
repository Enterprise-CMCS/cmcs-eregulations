from file_manager.admin import UploadedFileAdmin


def test_extension():
    file_name = 'blah.txt'
    admin = UploadedFileAdmin
    clean_name = admin.clean_file_name('', file_name)
    file_name = 'weird name with "quotations".doc'
    assert clean_name == 'blah.txt'
    clean_name = admin.clean_file_name('', file_name)
    assert clean_name == 'weird name with quotations.doc'
    file_name = "random:;/!? .xls"
    clean_name = admin.clean_file_name('', file_name)
    assert clean_name == 'random.xls'
