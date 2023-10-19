from content_search.models import ContentIndex
from file_manager.models import UploadedFile
from resources.models import FederalRegisterDocument, SupplementalContent


def check_index(content):
    '''
    Checks to see if the piece of content already has an index

    :param content:  Piece of resource
    '''
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
    '''
    update_index updates a piece of content if it already exist in the index

    :param content_index:  The existing index
    :param content: The content that was updated
    '''
    if isinstance(content, UploadedFile):
        new_index = ContentIndex(
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
        new_index.save()
    elif isinstance(content, SupplementalContent) or isinstance(content, FederalRegisterDocument):
        new_index = ContentIndex(
            category=content.category,
            url=content.url,
            doc_name_string=content.name,
            summary_string=content.description,
            date_string=content.date,
            resource_type='external',
        )
        new_index.save()
        if isinstance(content, SupplementalContent):
            new_index.supplemental_content = content
            new_index.content_type = 'supplementalcontent'
            new_index.content_id = content.id
        else:
            new_index.fr_doc = content
            new_index.content_type = 'federalregisterdocument'
            new_index.content_id = content.id
        new_index.save()
    new_index.content = content_index.content
    new_index.locations.set(content.locations.all())
    new_index.subjects.set(content.subjects.all())
    new_index.save()
    content_index.delete()
    return


def add_to_index(content):
    '''
    add_to_index is the main function for adding anything to the index. Identifies if it exist, if not create.
    If it does update the old one.

    param1 content: The content that was updated.
    '''
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


def index_group(resources):
    ''''
    Adds groups of content to the search index
    '''
    for res in resources:
        add_to_index(res)
