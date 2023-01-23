import json
from urllib.parse import unquote

import httpx

from .middleware import BaseMiddleware
from .options import ParametersNameDecodingHandlerOption


class ParametersNameDecodingHandler(BaseMiddleware):

    def __init__(
        self,
        options: ParametersNameDecodingHandlerOption = ParametersNameDecodingHandlerOption(),
        **kwargs
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
    ) -> httpx.Response:  #type: ignore
        """To execute the current middleware

        Args:
            request (httpx.Request): The prepared request object
            transport(httpx.AsyncBaseTransport): The HTTP transport to use

        Returns:
            Response: The response object.
        """
        current_options = self._get_current_options(request)

        updated_url: str = str(request.url)  #type: ignore
        if (
            current_options and current_options.enabled and '%' in updated_url
            and current_options.characters_to_decode
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
        current_options = self.options
        request_options = request.options.get(              # type:ignore
            ParametersNameDecodingHandlerOption.get_key()
        )
        # Override default options with request options
        if request_options:
            current_options = request_options

        return current_options
