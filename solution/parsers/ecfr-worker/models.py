from dataclasses import dataclass

from common.models import BackendCredentials

@dataclass
class EcfrPartConfig:
    title_number: int
    part_number: int
    credentials: BackendCredentials
