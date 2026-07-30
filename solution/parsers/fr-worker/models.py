from dataclasses import dataclass

from common.models import BackendCredentials


@dataclass
class FrDocumentConfig:
    document_number: str
    credentials: BackendCredentials
