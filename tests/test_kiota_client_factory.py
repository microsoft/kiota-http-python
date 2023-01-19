import httpx
import pytest

from kiota_http import middleware
from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_http.middleware import (
    AsyncKiotaTransport,
    MiddlewarePipeline,
    ParametersNameDecodingHandler,
    RedirectHandler,
    RetryHandler,
)
from kiota_http.middleware.options import RedirectHandlerOption, RetryHandlerOption


def test_create_with_default_middleware():
    """Test creation of HTTP Client using default middleware"""
    client = KiotaClientFactory.create_with_default_middleware()

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)


def test_create_with_default_middleware_options():
    """Test creation of HTTP Client using default middleware and custom options"""
    retry_options = RetryHandlerOption(max_retries=5)
    options = {f'{retry_options.get_key()}': retry_options}
    client = KiotaClientFactory.create_with_default_middleware(options=options)

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)
    pipeline = client._transport.pipeline
    assert isinstance(pipeline._first_middleware, RedirectHandler)
    retry_handler = pipeline._first_middleware.next
    assert isinstance(retry_handler, RetryHandler)
    assert retry_handler.max_retries == retry_options.max_retry


def test_create_with_custom_middleware():
    """Test creation of HTTP Clients with custom middleware"""
    middleware = [
        RetryHandler(),
    ]
    client = KiotaClientFactory.create_with_custom_middleware(middleware=middleware)

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)
    pipeline = client._transport.pipeline
    assert isinstance(pipeline._first_middleware, RetryHandler)


def test_get_default_middleware():
    """Test fetching of default middleware with no custom options passed"""
    middleware = KiotaClientFactory.get_default_middleware(None)

    assert len(middleware) == 3
    assert isinstance(middleware[0], RedirectHandler)
    assert isinstance(middleware[1], RetryHandler)
    assert isinstance(middleware[2], ParametersNameDecodingHandler)


def test_get_default_middleware_with_options():
    """Test fetching of default middleware with custom options passed"""
    retry_options = RetryHandlerOption(max_retries=7)
    redirect_options = RedirectHandlerOption(should_redirect=False)
    options = {
        f'{retry_options.get_key()}': retry_options,
        f'{redirect_options.get_key()}': redirect_options
    }

    middleware = KiotaClientFactory.get_default_middleware(options=options)

    assert len(middleware) == 3
    assert isinstance(middleware[0], RedirectHandler)
    assert middleware[0].should_redirect is False
    assert isinstance(middleware[1], RetryHandler)
    assert middleware[1].max_retries == 7
    assert isinstance(middleware[2], ParametersNameDecodingHandler)


def test_create_middleware_pipeline():

    middleware = KiotaClientFactory.get_default_middleware(None)
    pipeline = KiotaClientFactory.create_middleware_pipeline(
        middleware,
        httpx.AsyncClient()._transport
    )

    assert isinstance(pipeline, MiddlewarePipeline)
