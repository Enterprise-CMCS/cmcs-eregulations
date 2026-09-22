"""Shared Federal Register API exceptions for FR launcher and worker clients."""


class FedRegClientError(RuntimeError):
    """Raised for failed or malformed Federal Register API responses."""
