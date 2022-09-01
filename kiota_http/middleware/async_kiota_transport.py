import httpx


class AsyncKiotaTransport(httpx.AsyncBaseTransport):
    """A custom transport that implements Kiota middleware functionality
    """
    
    def __init__(self, transport: httpx.AsyncBaseTransport) -> None:
        self.transport = transport
        
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        # middleware = MiddleWarePipeline()
        # req = middleware.send(request)
        response = await self.transport.handle_async_request(request)
        return response 
