from typing import List, Set, Union

import httpx

from .middleware import BaseMiddleware
from .options import RedirectHandlerOption


class RedirectHandler(BaseMiddleware):
    """Middlware that allows us to define the redirect policy for all requests
    """

    DEFAULT_REDIRECT_STATUS_CODES: Set[int] = {
        301,  # Moved Permanently
        302,  # Found
        303,  # See Other
        307,  # Temporary Permanently
        308,  # Moved Permanently
    }
    STATUS_CODE_SEE_OTHER: int = 303
    LOCATION_HEADER: str = "Location"
    AUTHORIZATION_HEADER: str = "Authorization"

    def __init__(self, options: RedirectHandlerOption = RedirectHandlerOption()) -> None:
        super().__init__()
        self.should_redirect: bool = options.should_redirect
        self.max_redirects: int = options.max_redirect
        self.redirect_on_status_codes: Set[int] = self.DEFAULT_REDIRECT_STATUS_CODES
        self.history: List[httpx.Request] = []

    def get_redirect_location(self, response: httpx.Response) -> Union[str, bool, None]:
        """Checks for redirect status code and gets redirect location.
        Args:
            response(httpx.Response): The Response object

        Returns:
            Union[str, bool, None]: Truthy redirect location string if we got a redirect status
            code and valid location. ``None`` if redirect status and no
            location. ``False`` if not a redirect status code.
        """
        if response.status_code in [301, 302]:
            if response.next_request and response.next_request.method in [
                'GET',
                'HEAD',
            ]:
                return response.headers.get('location')
            return False
        if response.status_code in self.redirect_on_status_codes:
            return response.headers.get('location')

        return False

    def increment(self, response) -> bool:
        """Increment the redirect attempts for this request.

        Args
            response(httpx.Response): A httpx response object.

        Returns:
            bool: Whether further redirect attempts are remaining.
            False if exhausted; True if more redirect attempts available.
        """

        self.max_redirects -= 1
        self.history.append(response.request)

        if response.status_code == self.STATUS_CODE_SEE_OTHER:
            response.next_request.method = 'GET'
        if response.next_request:
            response.next_request.headers.pop(self.AUTHORIZATION_HEADER, None)
        return self.max_redirects >= 0

    async def send(
        self, request: httpx.Request, transport: httpx.AsyncBaseTransport
    ) -> httpx.Response:
        """Sends the http request object to the next middleware or redirects
        the request if necessary.
        """
        retryable = True
        while retryable:
            response = await super().send(request, transport)
            redirect_location = self.get_redirect_location(response)
            if redirect_location and self.should_redirect:
                retryable = self.increment(response)
                request = response.next_request
                continue
            return response

        raise Exception(f"Too many redirects. {response.history}")
