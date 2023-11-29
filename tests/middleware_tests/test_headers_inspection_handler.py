import pytest
import httpx

from unittest.mock import AsyncMock

from kiota_abstractions.headers_collection import HeadersCollection
from kiota_http.middleware.middleware import BaseMiddleware
from kiota_http.middleware.options.headers_inspection_handler_option import HeadersInspectionHandlerOption
from kiota_http.middleware.headers_inspection_handler import HeadersInspectionHandler


def test_no_config():
    """
    Ensures the Header Inspection defaults are set.
    """
    options = HeadersInspectionHandlerOption()
    assert options.inspect_request_headers
    assert options.inspect_response_headers
    assert isinstance(options.request_headers, HeadersCollection)


def test_custom_config():
    """
    Ensures that setting is_enabled to False.
    """

    options = HeadersInspectionHandlerOption(inspect_request_headers=False)
    assert not options.inspect_request_headers
    
    
def test_headers_inspection_handler_construction():
    """
    Ensures the Header Inspection handler instance is set.
    """
    handler = HeadersInspectionHandler()
    assert handler
    
@pytest.mark.asyncio
async def test_headers_inspection_handler_gets_headers(mock_async_transport):
    request = httpx.Request('GET', 'https://localhost', headers={'test': 'test_request_header'})
    handler = HeadersInspectionHandler()
    resp = await handler.send(request, mock_async_transport)
    assert resp.status_code == 200
    assert handler.options.request_headers.try_get('test') == {'test_request_header'}
    assert handler.options.response_headers.try_get('test') == {'test_response_header'}
    
    