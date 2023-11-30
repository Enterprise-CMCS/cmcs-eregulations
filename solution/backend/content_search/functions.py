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


def get_subject_string(subjects):
    if subjects:
        return ' '.join([f'{subject.full_name} '
                         f'{subject.short_name if subject.short_name else ""} '
                         f'{subject.abbreviation if subject.abbreviation else ""}' for subject in subjects])
    return ''


def upload_file_index(content):
    index = ContentIndex(
        file=content,
        document_type=content.document_type,
        file_name_string=content.file_name,
        url=content.uid,
        doc_name_string=content.document_name,
        summary_string=content.summary,
        date_string=content.date,
        resource_type='internal',
        rank_a_string=f"{content.document_name if content.document_name else ''}",
        rank_b_string=f"{content.summary if content.summary else ''}",
        rank_c_string=f"{content.date if content.date else ''} {content.file_name if content.file_name else ''}"
    )
    index.save()
    return index


def external_content_index(content):
    index = ContentIndex(
        category=content.category,
        url=content.url,
        doc_name_string=content.name,
        summary_string=content.description,
        date_string=content.date,
        resource_type='external',
        rank_a_string=f"{content.name if content.name else ''} {content.description if content.description else ''}",
        rank_b_string='',
        rank_c_string=f"{content.date if content.date else ''}"
    )
    index.save()
    return index


def add_to_index(content):
    '''
    add_to_index is the main function for adding anything to the index. Identifies if it exist, if not create.
    If it does update the old one.

    param1 content: The content that was updated.
    '''
    old_index = check_index(content)

    if isinstance(content, UploadedFile):
        content_index = upload_file_index(content)
        content_index.save()
    elif isinstance(content, SupplementalContent) or isinstance(content, FederalRegisterDocument):
        if not content.approved:
            if old_index:
                old_index.delete()
            return
        content_index = external_content_index(content)
        content_index.save()
        if isinstance(content, SupplementalContent):
            content_index.supplemental_content = content
        else:
            content_index.fr_doc = content
        content_index.save()
    content_index.rank_d_string = get_subject_string(content.subjects.all())
    content_index.locations.set(content.locations.all())
    content_index.subjects.set(content.subjects.all())
    if old_index:
        content_index.content = old_index.content
        old_index.delete()
    content_index.save()
    return None


def index_group(resources):
    ''''
    Adds groups of content to the search index
    '''
    for res in resources:
        add_to_index(res)
