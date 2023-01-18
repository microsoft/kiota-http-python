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
