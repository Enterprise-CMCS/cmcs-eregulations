from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.db import connections

from content_search.models import ContentIndex
from file_manager.models import DocumentType, Subject
from regcore.search.models import Synonym
from regulations.models import (
    RegulationLinkConfiguration,
    SiteConfiguration,
    StatuteLinkConfiguration,
    StatuteLinkConverter,
)
from resources.models import (
    AbstractCategory,
    AbstractLocation,
    AbstractResource,
    Category,
    FederalRegisterDocument,
    FederalRegisterDocumentGroup,
    ResourcesConfiguration,
    Section,
    SubCategory,
    Subpart,
    SupplementalContent,
)


def loadSeedData():
    fixtures = [
        ("regulations.siteconfiguration.json", SiteConfiguration),
        ("resources.abstractcategory.json", AbstractCategory),
        ("resources.category.json", Category),
        ("resources.subcategory.json", SubCategory),
        ("resources.abstractlocation.json", AbstractLocation),
        ("resources.subpart.json", Subpart),
        ("resources.section.json", Section),
        ("resources.abstractresource.json", AbstractResource),
        ("resources.supplementalcontent.json", SupplementalContent),
        ("resources.federalregisterdocumentgroup.json", FederalRegisterDocumentGroup),
        ("resources.federalregisterdocument.json", FederalRegisterDocument),
        ("resources.resourcesconfiguration.json", ResourcesConfiguration),
        ("search.synonym.json", Synonym),
        ("regulations.regulationlinkconfiguration.json", RegulationLinkConfiguration),
        ("regulations.statutelinkconverter.json", StatuteLinkConverter),
        ("regulations.statutelinkconfiguration.json", StatuteLinkConfiguration),
        ("file_manager.documenttype.json", DocumentType),
        ("file_manager.subject.json", Subject),
        ("content_search.contentindex.json", ContentIndex),
        ("cmcs_regulations/fixtures/contenttypes.contenttype.json", ContentType),
        ("cmcs_regulations/fixtures/auth.permission.json", Permission),
        ("cmcs_regulations/fixtures/auth.group.json", Group),
    ]
    # The vector column for the search index has issues with using seed data.  As in it takes forever.
    # We remove the column first, then we add it back after fixtures are done.

    cursor = connections['default'].cursor()
    cursor.execute('''ALTER TABLE content_search_contentindex DROP COLUMN vector_column;''')
    for fixture in reversed(fixtures):
        fixture[1].objects.all().delete()

    for fixture in fixtures:
        call_command("loaddata", fixture[0])
    cursor = connections['default'].cursor()
    cursor.execute('''
              ALTER TABLE content_search_contentindex ADD COLUMN vector_column tsvector GENERATED ALWAYS AS (
                setweight(to_tsvector('english', coalesce(doc_name_string, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(summary_string,'')), 'A') ||
                setweight(to_tsvector('english', coalesce(file_name_string,'')), 'C') ||
                setweight(to_tsvector('english', coalesce(date_string,'')), 'C') ||
                setweight(to_tsvector('english', coalesce(content,'')), 'D')
              ) STORED;
              CREATE INDEX content_search_index_vec ON content_search_contentindex USING GIN (vector_column);
            ''')
