from typing import Any

from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.response_handler import ResponseHandler


class ResponseHandlerOption(RequestOption):
    """ Adds a ResponseHandler as a RequestOption for the request."""

    RESPONSE_HANDLER_OPTION_KEY = "ResponseHandler"

    def __init__(self, response_handler: ResponseHandler = None) -> None:
        """To create an instance of ResponseHandlerOption

        Args:
            response_handler (ResponseHandler): - The response handler instance
        """
        self._response_handler = response_handler

    @property
    def response_handler(self):
        """Property to return the response handler instance"""
        return self._response_handler

    def get_key(self):
        return self.RESPONSE_HANDLER_OPTION_KEY
