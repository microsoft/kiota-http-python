from httpx import AsyncBaseTransport, Request, Response
from kiota_abstractions.request_option import RequestOption

from .middleware import BaseMiddleware
from .options import UserAgentHandlerOption


class UserAgentHandler(BaseMiddleware):
    """
    Middleware handler for User Agent.
    """

    def __init__(self, options: RequestOption = UserAgentHandlerOption(), **kwargs):
        super().__init__(**kwargs)
        self.options = UserAgentHandlerOption() if options is None else options

    async def send(self, request: Request, transport: AsyncBaseTransport) -> Response:
        """
        Checks if the request has a User-Agent header and updates it if the
        platform config allows.
        """
        if self.options and self.options.is_enabled:
            value = f"{self.options.product_name}/{self.options.product_version}"

            user_agent = request.headers.get("User-Agent", "")
            if not user_agent:
                request.headers.update({"User-Agent": value})
            else:
                if value not in user_agent:
                    request.headers.update({"User-Agent": f"{user_agent} {value}"})

        return await super().send(request, transport)
