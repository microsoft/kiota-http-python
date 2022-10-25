import httpx
import pytest

from kiota_http.kiota_client import KiotaClient


def test_create_client():
    """
    Test creating a Kiota client with default middleware works as expected
    """
    client = KiotaClient().client

    assert isinstance(client, httpx.AsyncClient)


def test_kiota_client_uses_same_session():
    """
    Test kiota client is a singleton class and uses the same session(TCP connection)
    """
    client = KiotaClient()
    client2 = KiotaClient()
    assert client is client2
