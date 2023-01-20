from __future__ import annotations

from typing import Dict, List, Optional

import httpx
from kiota_abstractions.request_option import RequestOption

from .middleware import (
    AsyncKiotaTransport,
    BaseMiddleware,
    MiddlewarePipeline,
    ParametersNameDecodingHandler,
    RedirectHandler,
    RetryHandler,
)
from .middleware.options import (
    ParametersNameDecodingHandlerOption,
    RedirectHandlerOption,
    RetryHandlerOption,
)

DEFAULT_CONNECTION_TIMEOUT: int = 30
DEFAULT_REQUEST_TIMEOUT: int = 100


class KiotaClientFactory:

    @staticmethod
    def get_default_client() -> httpx.AsyncClient:
        """Returns a native HTTP AsyncClient(httpx.AsyncClient) instance with default options

        Returns:
            httpx.AsyncClient
        """
        timeout = httpx.Timeout(DEFAULT_REQUEST_TIMEOUT, connect=DEFAULT_CONNECTION_TIMEOUT)
        return httpx.AsyncClient(timeout=timeout, http2=True)

    @staticmethod
    def create_with_default_middleware(
        options: Optional[Dict[str, RequestOption]] = None
    ) -> httpx.AsyncClient:
        """Constructs native HTTP AsyncClient(httpx.AsyncClient) instances configured with
        a custom transport loaded with a default pipeline of middleware.

        Args:
            options (Optional[Dict[str, RequestOption]]): The request options to use when
            instantiating default middleware. Defaults to Dict[str, RequestOption]=None.

        Returns:
            httpx.AsycClient: An instance of the AsyncClient object
        """

        kiota_async_client = KiotaClientFactory.get_default_client()
        current_transport = kiota_async_client._transport
        middleware = KiotaClientFactory.get_default_middleware(options)
        middleware_pipeline = KiotaClientFactory.create_middleware_pipeline(
            middleware, current_transport
        )

        kiota_async_client._transport = AsyncKiotaTransport(
            transport=current_transport, pipeline=middleware_pipeline
        )
        return kiota_async_client

    @staticmethod
    def create_with_custom_middleware(
        middleware: Optional[List[BaseMiddleware]],
    ) -> httpx.AsyncClient:
        """Constructs native HTTP AsyncClient(httpx.AsyncClient) instances configured with
        a custom pipeline of middleware.

        Args:
            middleware(List[BaseMiddleware]): Custom middleware list that will be used to create
            a middleware pipeline. The middleware should be arranged in the order in which they will
            modify the request.
        """
        kiota_async_client = KiotaClientFactory.get_default_client()
        current_transport = kiota_async_client._transport
        middleware_pipeline = KiotaClientFactory.create_middleware_pipeline(
            middleware, current_transport
        )

        kiota_async_client._transport = AsyncKiotaTransport(
            transport=current_transport, pipeline=middleware_pipeline
        )
        return kiota_async_client

    @staticmethod
    def get_default_middleware(options: Optional[Dict[str, RequestOption]]) -> List[BaseMiddleware]:
        """
        Helper method that returns a list of default middleware instantiated with
        appropriate options
        """
        redirect_handler = RedirectHandler()
        retry_handler = RetryHandler()
        parameters_name_decoding_handler = ParametersNameDecodingHandler()

        if options:
            redirect_handler_options = options.get(RedirectHandlerOption().get_key())
            if redirect_handler_options:
                redirect_handler = RedirectHandler(options=redirect_handler_options)

            retry_handler_options = options.get(RetryHandlerOption().get_key())
            if retry_handler_options:
                retry_handler = RetryHandler(options=retry_handler_options)

            parameters_name_decoding_handler_options = options.get(
                ParametersNameDecodingHandlerOption().get_key()
            )
            if parameters_name_decoding_handler_options:
                parameters_name_decoding_handler = ParametersNameDecodingHandler(
                    options=parameters_name_decoding_handler_options
                )

        middleware = [redirect_handler, retry_handler, parameters_name_decoding_handler]
        return middleware

    @staticmethod
    def create_middleware_pipeline(
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
