
from django.db import models

from file_manager.models import UploadedFile


class FileIndex(models.Model):
    doc_name_string = models.CharField(max_length=512, null=True, blank=True)
    summary_string = models.CharField(max_length=512, null=True, blank=True)
    subject_string = models.CharField(max_length=512, null=True, blank=True)
    file_name_string = models.CharField(max_length=512, null=True, blank=True)
    doc_type_string = models.CharField(max_length=512, null=True, blank=True)
    date_string = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField()
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)


def subject_string(subjects):
    subject_string = ''
    for subject in subjects:
        text_string = ''
        if subject.full_name:
            text_string = subject.full_name
        if subject.abbreviation:
            text_string = text_string + ' ' + subject.abbreviation
        subject_string = subject_string + ' ' + text_string
    return subject_string


def create_search(updated_doc, file=None):
    subjects = subject_string(updated_doc.subject.all())
    file_content = ''
    if file:
        file_content = file.content
    else:
        # Trigger lambda here to get the text
        file_content = ''
    fi = FileIndex(
        doc_name_string=updated_doc.document_id,
        summary_string=updated_doc.summary,
        subject_string=subjects,
        file_name_string=updated_doc.file_name,
        doc_type_string=str(updated_doc.document_type),
        date_string=updated_doc.date,
        content=file_content,
        file=updated_doc
    )
    fi.save()


def update_search(sender, instance, created, **kwargs):
    try:
        file = FileIndex.objects.get(file=instance)
        create_search(instance, file)
        file.delete()
    except FileIndex.DoesNotExist:
        create_search(instance)
