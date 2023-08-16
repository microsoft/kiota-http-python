from urllib.parse import unquote

import httpx
from kiota_abstractions.request_option import RequestOption

from .middleware import BaseMiddleware
from .options import ParametersNameDecodingHandlerOption

PARAMETERS_NAME_DECODING_KEY = "com.microsoft.kiota.handler.parameters_name_decoding.enable"


class ParametersNameDecodingHandler(BaseMiddleware):

    def __init__(
        self,
        options: RequestOption = ParametersNameDecodingHandlerOption(),
    ):
        """Create an instance of ParametersNameDecodingHandler

        Args:
            options (ParametersNameDecodingHandlerOption, optional): The parameters name
            decoding handler options value.
            Defaults to ParametersNameDecodingHandlerOption
        """
        super().__init__()
        self.options = options

    async def send(
        self, request: httpx.Request, transport: httpx.AsyncBaseTransport
    ) -> httpx.Response:  # type: ignore
        """To execute the current middleware

        Args:
            request (httpx.Request): The prepared request object
            transport(httpx.AsyncBaseTransport): The HTTP transport to use

        Returns:
            Response: The response object.
        """
        current_options = self._get_current_options(request)
        span = self._create_observability_span(request, "ParametersNameDecodingHandler_send")
        if current_options.enabled:
            span.set_attribute(PARAMETERS_NAME_DECODING_KEY, current_options.enabled)
        span.end()

        updated_url: str = str(request.url)  # type: ignore
        if all(
            [
                current_options, current_options.enabled, '%' in updated_url,
                current_options.characters_to_decode
            ]
        ):
            updated_url = unquote(updated_url)
        request.url = httpx.URL(updated_url)
        response = await super().send(request, transport)
        return response

    def _get_current_options(self, request: httpx.Request) -> ParametersNameDecodingHandlerOption:
        """Returns the options to use for the request.Overries default options if
        request options are passed.

        Args:
            request (httpx.Request): The prepared request object

        Returns:
            ParametersNameDecodingHandlerOption: The options to used.
        """
        if options := getattr(request, 'options', None):
            current_options = options.get(  # type:ignore
                ParametersNameDecodingHandlerOption.get_key(), self.options
            )
        return current_options

    def decode_uri_encoded_string(self, original: str) -> str:
        """Decodes a uri encoded string ."""
        if original and '%' in original:
            return unquote(original)
        return original
