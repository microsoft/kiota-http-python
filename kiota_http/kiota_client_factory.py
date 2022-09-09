import functools
from sqlite3 import connect

import httpx

from .middleware import (
    AsyncKiotaTransport,
    MiddlewarePipeline,
    ParametersNameDecodingHandler,
    RedirectHandler,
    RetryHandler,
)


class KiotaClientFactory:
    DEFAULT_CONNECTION_TIMEOUT: int = 30
    DEFAULT_REQUEST_TIMEOUT: int = 100

    def create_with_default_middleware(self) -> httpx.AsyncClient:
        """Constructs native HTTP AsyncClient(httpx.AsyncClient) instances configured with
        a custom transport loaded with a default pipeline of middleware.

        Returns:
            httpx.AsycClient: An instance of the AsyncClient object
        """
        timeout = httpx.Timeout(
            self.DEFAULT_REQUEST_TIMEOUT, connect=self.DEFAULT_CONNECTION_TIMEOUT
        )
        kiota_async_client = httpx.AsyncClient(timeout=timeout, http2=True)
        current_transport = kiota_async_client._transport
        middleware = self._get_default_middleware(current_transport)

        kiota_async_client._transport = AsyncKiotaTransport(
            transport=current_transport, middleware=middleware
        )
        return kiota_async_client

    def _get_default_middleware(self, transport: httpx.AsyncBaseTransport) -> MiddlewarePipeline:
        """
        Helper method that constructs a middleware_pipeline with the specified middleware
        """
        middleware_pipeline = MiddlewarePipeline(transport)
        middlewares = [
            ParametersNameDecodingHandler(),
            RetryHandler(),
            RedirectHandler(),
        ]

        for middleware in middlewares:
            middleware_pipeline.add_middleware(middleware)

        return middleware_pipeline
