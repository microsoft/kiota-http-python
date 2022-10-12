import httpx
import pytest

from kiota_http.middleware import RedirectHandler
from kiota_http.middleware.options import RedirectHandlerOption

BASE_URL = 'https://httpbin.org'
REDIRECT_URL = "https://graph.microsoft.com"


def test_no_config():
    """
    Test that default values are used if no custom confguration is passed
    """
    options = RedirectHandlerOption()
    handler = RedirectHandler()
    assert handler.should_redirect == options.should_redirect
    assert handler.max_redirects == options.max_redirect
    assert handler.redirect_on_status_codes == handler.DEFAULT_REDIRECT_STATUS_CODES


def test_custom_options():
    """
    Test that default configuration is overrriden if custom configuration is provided
    """
    options = RedirectHandlerOption()
    options.max_redirect = 3
    options.should_redirect = False

    handler = RedirectHandler(options)

    assert handler.max_redirects == 3
    assert not handler.should_redirect


def test_increment_redirects():
    """
    Tests that redirect are incremented
    """
    request = httpx.Request('GET', BASE_URL)
    response = httpx.Response(301, request=request)

    handler = RedirectHandler()
    assert handler.increment(response)
