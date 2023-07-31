"""Exceptions raised in Kiota HTTP."""


class KiotaHTTPException(Exception):
    """Base class for Kiota HTTP exceptions."""


class BackingstoreException(KiotaHTTPException):
    """Raised for the backing store."""


class DeserializationException(KiotaHTTPException):
    """Raised for deserialization."""
