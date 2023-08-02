from httpx import AsyncBaseTransport, Request, Response
from kiota_abstractions.request_option import RequestOption
from opentelemetry.semconv.trace import SpanAttributes

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
        _span = self._create_observability_span(request, "UserAgentHandler_send")
        if self.options and self.options.is_enabled:
            _span.set_attribute("com.microsoft.kiota.handler.useragent.enable", True)
            value = f"{self.options.product_name}/{self.options.product_version}"
            self._update_user_agent(request, value)
        _span.end()
        return await super().send(request, transport)

    def _update_user_agent(self, request: Request, value: str):
        """Updates the values of the User-Agent header."""
        user_agent = request.headers.get("User-Agent", "")
        if not user_agent:
            request.headers.update({"User-Agent": value})
        else:
            if value not in user_agent:
                request.headers.update({"User-Agent": f"{user_agent} {value}"})
