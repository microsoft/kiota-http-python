import functools

import httpx

from .middleware import MiddlewarePipeline, ParametersNameDecodingHandler, RetryHandler


class KiotaClientFactory:
    DEFAULT_CONNECTION_TIMEOUT: int = 30
    DEFAULT_REQUEST_TIMEOUT: int = 100

    async def create_with_default_middleware(self) -> httpx.AsyncClient:
        """Constructs native HTTP AsyncClient(httpx.AsyncClient) instances configured with a default
        pipeline of middleware.

        Returns:
            httpx.AsycClient: An instance of the AsyncClient object
        """
        timeout = httpx.Timeout(self.DEFAULT_CONNECTION_TIMEOUT, self.DEFAULT_REQUEST_TIMEOUT)
        httpx_async_client = httpx.AsyncClient(timeout=timeout)
        async with httpx_async_client as client:
            return self._register_default_middleware(client)

    def _register_default_middleware(self, session: httpx.AsyncClient) -> httpx.AsyncClient:
        """
        Helper method that constructs a middleware_pipeline with the specified middleware
        """
        middleware_pipeline = MiddlewarePipeline()
        middlewares = [
            ParametersNameDecodingHandler(),
            RetryHandler(),
        ]

        for middleware in middlewares:
            middleware_pipeline.add_middleware(middleware)

        session.mount('https://', middleware_pipeline)
        return session
