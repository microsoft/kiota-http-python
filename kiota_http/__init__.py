"""
Kiota http request adapter implementation for httpx library
"""
from ._version import VERSION
from .httpx_request_adapter import HttpxRequestAdapter
from .kiota_client import KiotaClient
from .kiota_client_factory import KiotaClientFactory

__version__ = VERSION
