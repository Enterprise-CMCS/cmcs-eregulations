"""Custom exceptions for eCFR XML parser pipeline."""


class EcfrXmlParseError(RuntimeError):
    """Raised when raw XML cannot be parsed or normalized for eRegs."""

    pass
