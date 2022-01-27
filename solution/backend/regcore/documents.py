from django_opensearch_dsl import Document, fields
from django_opensearch_dsl.registries import registry
from .models import Part


@registry.register_document
class PartDocument(Document):

    document_text = fields.TextField(attr='document_text')
    toc = fields.TextField(attr='toc')
    structure_text = fields.TextField(attr='structure_text')

    class Index:
        name = 'part'

    class Django:
        model = Part
        fields = [
            'name',
            'title',
            'date',
        ]
