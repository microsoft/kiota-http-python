from __future__ import annotations

from typing import List, Optional

import httpx

from .middleware import (
    AsyncKiotaTransport,
    BaseMiddleware,
    MiddlewarePipeline,
    ParametersNameDecodingHandler,
    RedirectHandler,
    RetryHandler,
)

DEFAULT_CONNECTION_TIMEOUT: int = 30
DEFAULT_REQUEST_TIMEOUT: int = 100


class KiotaClientFactory:

    @staticmethod
    def create_with_default_middleware() -> httpx.AsyncClient:
        """Constructs native HTTP AsyncClient(httpx.AsyncClient) instances configured with
        a custom transport loaded with a default pipeline of middleware.

        Returns:
            httpx.AsycClient: An instance of the AsyncClient object
        """
        timeout = httpx.Timeout(DEFAULT_REQUEST_TIMEOUT, connect=DEFAULT_CONNECTION_TIMEOUT)
        kiota_async_client = httpx.AsyncClient(timeout=timeout, http2=True)
        current_transport = kiota_async_client._transport
        middleware = KiotaClientFactory._get_default_middleware()
        middleware_pipeline = KiotaClientFactory._create_middleware_pipeline(
            middleware, current_transport
        )

        kiota_async_client._transport = AsyncKiotaTransport(
            transport=current_transport, pipeline=middleware_pipeline
        )
        return kiota_async_client

    @staticmethod
    def _get_default_middleware() -> List[BaseMiddleware]:
        """
        Helper method that returns a list of default middleware
        """
        middleware = [RedirectHandler(), RetryHandler(), ParametersNameDecodingHandler()]

        return middleware

    @staticmethod
    def _create_middleware_pipeline(
        middleware: Optional[List[BaseMiddleware]], transport: httpx.AsyncBaseTransport
    ) -> MiddlewarePipeline:
        """
        Helper method that constructs a middleware_pipeline with the specified middleware
        """
        middleware_pipeline = MiddlewarePipeline(transport)
        if middleware:
            for ware in middleware:
                middleware_pipeline.add_middleware(ware)
        return middleware_pipeline
