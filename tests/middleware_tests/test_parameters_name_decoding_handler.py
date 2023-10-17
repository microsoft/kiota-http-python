import httpx
import pytest

from kiota_http.middleware import ParametersNameDecodingHandler
from kiota_http.middleware.options import ParametersNameDecodingHandlerOption


def test_no_config():
    """
    Test that default values are used if no custom confguration is passed
    """
    handler = ParametersNameDecodingHandler()
    assert handler.options.enabled is True
    assert handler.options.characters_to_decode == [".", "-", "~", "$"]
    assert handler.options.get_key() == "ParametersNameDecodingHandlerOption"


def test_custom_options():
    """
    Test that default configuration is overrriden if custom configuration is provided
    """
    options = ParametersNameDecodingHandlerOption(enable=False, characters_to_decode=[".", "-"])
    handler = ParametersNameDecodingHandler(options)

    assert handler.options.enabled is not True
    assert "$" not in handler.options.characters_to_decode
    assert handler.options.get_key() == "ParametersNameDecodingHandlerOption"

@pytest.mark.asyncio
async def test_decodes_query_parameter_names_only():
    """
    Test that only query parameter names are decoded
    """
    encoded_url = 'https://graph.microsoft.com?%24count=true&query=%24top&created%2din=2022-10-05&q=1%2b2&q2=M%26A&subject%2ename=%7eWelcome'
    expected_url = 'https://graph.microsoft.com?$count=true&query=%24top&created-in=2022-10-05&q=1%2b2&q2=M%26A&subject.name=%7eWelcome'
    def request_handler(request: httpx.Request):
        assert str(request.url) == expected_url
        return httpx.Response(200, json={"text": "Hello, world!"})
    handler = ParametersNameDecodingHandler()
    request = httpx.Request('GET', encoded_url)
    mock_transport = httpx.MockTransport(request_handler)
    await handler.send(request, mock_transport)
