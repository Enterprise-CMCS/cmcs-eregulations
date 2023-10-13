from content_search.models import ContentIndex
from file_manager.models import UploadedFile
from resources.models import FederalRegisterDocument, SupplementalContent


def check_index(content):
    content_index = None
    try:
        if isinstance(content, UploadedFile):
            content_index = ContentIndex.objects.get(file=content)
        elif isinstance(content, SupplementalContent):
            content_index = ContentIndex.objects.get(supplemental_content=content)
        elif isinstance(content, FederalRegisterDocument):
            content_index = ContentIndex.objects.get(fr_doc=content)
        return content_index
    except ContentIndex.DoesNotExist:
        return None


def update_index(content_index, content):
    if isinstance(content, UploadedFile):
        content_index.document_type = content.document_type
        content_index.file_name_string = content.file_name
        content_index.url = content.uid
        content_index.doc_name_string = content.document_name
        content_index.summary_string = content.summary
        content_index.date_string = content.date
    elif isinstance(content, SupplementalContent) or isinstance(content, FederalRegisterDocument):
        content_index.category = content.category
        content_index.url = content.url
        content_index.doc_name_string = content.name
        content_index.summary_string = content.description
        content_index.date_string = content.date
    content_index.locations.set(content.locations.all())
    content_index.subjects.set(content.subjects.all())
    content_index.save()
    return


def add_to_index(content):
    content_index = check_index(content)
    if content_index:
        return update_index(content_index, content)
    if isinstance(content, UploadedFile):
        content_index = ContentIndex(
            file=content,
            document_type=content.document_type,
            file_name_string=content.file_name,
            url=content.uid,
            doc_name_string=content.document_name,
            summary_string=content.summary,
            date_string=content.date,
            resource_type='internal',
            content_type='uploadedfile',
            content_id=content.id
        )
        content_index.save()
    elif isinstance(content, SupplementalContent) or isinstance(content, FederalRegisterDocument):
        content_index = ContentIndex(
            category=content.category,
            url=content.url,
            doc_name_string=content.name,
            summary_string=content.description,
            date_string=content.date,
            resource_type='external',
        )

        if isinstance(content, SupplementalContent):
            content_index.supplemental_content = content
            content_index.content_type = 'supplementalcontent'
            content_index.content_id = content.id
        else:
            content_index.fr_doc = content
            content_index.content_type = 'federalregisterdocument'
            content_index.content_id = content.id
        content_index.save()
    content_index.locations.set(content.locations.all())
    content_index.subjects.set(content.subjects.all())
    content_index.save()
    return None
