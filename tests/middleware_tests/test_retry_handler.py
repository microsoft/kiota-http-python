from email.utils import formatdate
from time import time

import httpx
import pytest

from kiota_http.middleware import RetryHandler
from kiota_http.middleware.options import RetryHandlerOption

BASE_URL = 'https://httpbin.org'


def test_no_config():
    """
    Test that default values are used if no custom confguration is passed
    """
    options = RetryHandlerOption()
    retry_handler = RetryHandler()
    assert retry_handler.max_retries == options.max_retry
    assert retry_handler.timeout == options.max_delay
    assert retry_handler.allowed_methods == frozenset(
        ['HEAD', 'GET', 'PUT', 'POST', 'PATCH', 'DELETE', 'OPTIONS']
    )
    assert retry_handler.respect_retry_after_header


def test_custom_options():
    """
    Test that default configuration is overrriden if custom configuration is provided
    """
    options = RetryHandlerOption()
    options.max_retry = 1
    options.max_delay = 100
    options.should_retry = False

    retry_handler = RetryHandler(options)

    assert retry_handler.max_retries == 1
    assert retry_handler.timeout == 100
    assert not retry_handler.retries_allowed


def test_method_retryable_with_valid_method():
    """
    Test if method is retryable with a retryable request method.
    """
    request = httpx.Request('GET', BASE_URL)
    retry_handler = RetryHandler()
    assert retry_handler._is_method_retryable(request)


def test_should_retry_valid():
    """
    Test the should_retry method with a valid HTTP method and response code
    """
    request = httpx.Request('GET', BASE_URL)
    response = httpx.Response(503)

    retry_handler = RetryHandler()
    assert retry_handler.should_retry(request, response)


def test_should_retry_invalid():
    """
    Test the should_retry method with an invalid HTTP response code
    """
    request = httpx.Request('GET', BASE_URL)
    response = httpx.Response(502)

    retry_handler = RetryHandler()

    assert not retry_handler.should_retry(request, response)


def test_is_request_payload_buffered_valid():
    """
    Test for _is_request_payload_buffered helper method.
    Should return true request payload is buffered/rewindable.
    """
    request = httpx.Request('GET', BASE_URL)

    retry_handler = RetryHandler()

    assert retry_handler._is_request_payload_buffered(request)


def test_is_request_payload_buffered_invalid():
    """
    Test for _is_request_payload_buffered helper method.
    Should return false if request payload is forward streamed.
    """
    request = httpx.Request('POST', BASE_URL, headers={'Content-Type': "application/octet-stream"})

    retry_handler = RetryHandler()

    assert not retry_handler._is_request_payload_buffered(request)


def test_check_retry_valid():
    """
    Test that a retry is valid if the maximum number of retries has not been reached
    """
    retry_handler = RetryHandler()

    assert retry_handler.check_retry_valid(0)


def test_check_retry_valid_no_retries():
    """
    Test that a retry is not valid if maximum number of retries has been reached
    """
    options = RetryHandlerOption()
    options.max_retry = 2
    retry_handler = RetryHandler(options)

    assert not retry_handler.check_retry_valid(2)


def test_get_retry_after():
    """
    Test the _get_retry_after method with an integer value for retry header.
    """
    response = httpx.Response(503, headers={'Retry-After': "120"})
    retry_handler = RetryHandler()

    assert retry_handler._get_retry_after(response) == 120


def test_get_retry_after_no_header():
    """
    Test the _get_retry_after method with no Retry-After header.
    """
    response = httpx.Response(503)

    retry_handler = RetryHandler()

    assert retry_handler._get_retry_after(response) is None


def test_get_retry_after_http_date():
    """
    Test the _get_retry_after method with a http date as Retry-After value.
    """
    timevalue = time() + 120
    http_date = formatdate(timeval=timevalue, localtime=False, usegmt=True)
    response = httpx.Response(503, headers={'retry-after': f'{http_date}'})

    retry_handler = RetryHandler()
    assert retry_handler._get_retry_after(response) < 120
