import httpx
import pytest

from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_http.middleware import AsyncKiotaTransport, MiddlewarePipeline


def test_create_with_default_middleware():
    """Test creation of HTTP Client using default middleware"""
    client = KiotaClientFactory().create_with_default_middleware()

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)


def test_get_default_middleware():
    client = KiotaClientFactory().create_with_default_middleware()
    middleware = KiotaClientFactory()._get_default_middleware(client._transport)
    assert isinstance(middleware, MiddlewarePipeline)
