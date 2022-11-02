import ssl

import httpx
from urllib3 import PoolManager


class MiddlewarePipeline():
    """MiddlewarePipeline, entry point of middleware
    The pipeline is implemented as a linked-list, read more about
    it here https://buffered.dev/middleware-python-requests/
    """

    def __init__(self, transport: httpx.AsyncBaseTransport):
        super().__init__()
        self._current_middleware = None
        self._first_middleware = None
        self._transport = transport
        self.poolmanager = PoolManager(ssl_version=ssl.PROTOCOL_TLSv1_2)

    def add_middleware(self, middleware):
        if self._middleware_present():
            self._current_middleware.next = middleware
            self._current_middleware = middleware
        else:
            self._first_middleware = middleware
            self._current_middleware = self._first_middleware

    async def send(self, request):

        if self._middleware_present():
            return await self._first_middleware.send(request, self._transport)
        # No middleware in pipeline, delete request optoions from header and
        # send the request
        del request.headers['request_options']
        return await self._transport.handle_async_request(request)

    def _middleware_present(self):
        return self._current_middleware


class BaseMiddleware():
    """Base class for middleware. Handles moving a Request to the next middleware in the pipeline.
    If the current middleware is the last one in the pipeline, it makes a network request
    """

    def __init__(self):
        self.next = None

    async def send(self, request, transport):
        if self.next is None:
            # Remove request options. No longer needed.
            if 'request_options' in request.headers:
                del request.headers['request_options']
            response = await transport.handle_async_request(request)
            response.request = request
            return response
        return await self.next.send(request, transport)
