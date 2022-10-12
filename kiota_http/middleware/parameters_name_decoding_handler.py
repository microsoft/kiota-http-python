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
            request (PreparedRequest): The prepared request object
            request_options (Dict[str, RequestOption]): The request options

        Returns:
            Response: The response object.
        """
        current_options = self.options
        options_key = (
            ParametersNameDecodingHandlerOption.PARAMETERS_NAME_DECODING_HANDLER_OPTION_KEY
        )
        request_options = json.loads(request.headers['request_options'])
        if request_options and options_key in request_options:
            current_options = request_options[options_key]

        updated_url: str = str(request.url)  #type: ignore
        if (
            current_options and current_options.enabled and '%' in updated_url
            and current_options.characters_to_decode
        ):
            updated_url = unquote(updated_url)
        request.url = httpx.URL(updated_url)
        response = await super().send(request, transport)
        return response
