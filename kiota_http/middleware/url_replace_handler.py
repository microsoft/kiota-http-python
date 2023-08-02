import httpx
from kiota_abstractions.request_option import RequestOption
from opentelemetry import trace
from opentelemetry.semconv.trace import SpanAttributes

from .._version import VERSION
from ..observability_options import ObservabilityOptions
from .middleware import BaseMiddleware
from .options import UrlReplaceHandlerOption

tracer = trace.get_tracer(ObservabilityOptions.get_tracer_instrumentation_name(), VERSION)


class UrlReplaceHandler(BaseMiddleware):

    def __init__(self, options: RequestOption = UrlReplaceHandlerOption()):
        """Create an instance of UrlReplaceHandler

        Args:
            options (UrlReplaceHandlerOption, optional): The url replacement
            options to pass to the handler.
            Defaults to UrlReplaceHandlerOption
        """
        super().__init__()
        self.options = options

    async def send(
        self, request: httpx.Request, transport: httpx.AsyncBaseTransport
    ) -> httpx.Response:  #type: ignore
        """To execute the current middleware

        Args:
            request (httpx.Request): The prepared request object
            transport(httpx.AsyncBaseTransport): The HTTP transport to use

        Returns:
            Response: The response object.
        """
        response: httpx.Response
        if options := getattr(request, "options", None):
            if parent_span := options.get("parent_span", None):
                _context = trace.set_span_in_context(parent_span)
                _enable_span = tracer.start_span("UrlReplaceHandler_send", _context)
                _enable_span.set_attribute("com.microsoft.kiota.handler.url_replacer.enable", True)
                current_options = self._get_current_options(request)

                url_string: str = str(request.url)  #type: ignore
                url_string = self.replace_url_segment(url_string, current_options)
                request.url = httpx.URL(url_string)
                _enable_span.set_attribute(SpanAttributes.HTTP_URL, str(request.url))
                response = await super().send(request, transport)
                _enable_span.end()
        return response

    def _get_current_options(self, request: httpx.Request) -> UrlReplaceHandlerOption:
        """Returns the options to use for the request.Overries default options if
        request options are passed.

        Args:
            request (httpx.Request): The prepared request object

        Returns:
            UrlReplaceHandlerOption: The options to be used.
        """
        current_options =request.options.get(  # type:ignore
            UrlReplaceHandlerOption.get_key(), self.options
        )
        return current_options

    def replace_url_segment(self, url_str: str, current_options: UrlReplaceHandlerOption) -> str:
        if all([current_options, current_options.is_enabled, current_options.replacement_pairs]):
            for k, v in current_options.replacement_pairs.items():
                url_str = url_str.replace(k, v, 1)
        return url_str
