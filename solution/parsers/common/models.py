from dataclasses import dataclass


@dataclass
class BackendCredentials:
    auth_type: str
    username: str | None = None
    password: str | None = None
    token: str | None = None
