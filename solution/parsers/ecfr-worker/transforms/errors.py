"""Shared transform exceptions for eCFR worker structure processing."""


class EcfrTransformError(RuntimeError):
    """Raised when required structure nodes cannot be located or parsed."""

    pass
