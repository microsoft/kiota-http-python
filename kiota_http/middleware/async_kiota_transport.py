import httpx

from .middleware import MiddlewarePipeline


class AsyncKiotaTransport(httpx.AsyncBaseTransport):
    """A custom transport that implements Kiota middleware functionality
    """

    def __init__(self, transport: httpx.AsyncBaseTransport, middleware: MiddlewarePipeline) -> None:
        self.transport = transport
        self.middleware = middleware

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if self.middleware:
            response = await self.middleware.send(request)
            return response

        response = await self.transport.handle_async_request(request)
        return response
