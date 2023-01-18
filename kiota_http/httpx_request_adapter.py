from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar

import httpx
from kiota_abstractions.api_client_builder import (
    enable_backing_store_for_parse_node_factory,
    enable_backing_store_for_serialization_writer_factory,
)
from kiota_abstractions.api_error import APIError
from kiota_abstractions.authentication import AuthenticationProvider
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import (
    Parsable,
    ParsableFactory,
    ParseNode,
    ParseNodeFactory,
    ParseNodeFactoryRegistry,
    SerializationWriterFactory,
    SerializationWriterFactoryRegistry,
)
from kiota_abstractions.store import BackingStoreFactory, BackingStoreFactorySingleton

from .kiota_client_factory import KiotaClientFactory
from .middleware.options import ResponseHandlerOption

ResponseType = TypeVar("ResponseType", str, int, float, bool, datetime, bytes)
ModelType = TypeVar("ModelType", bound=Parsable)


class HttpxRequestAdapter(RequestAdapter):

    def __init__(
        self,
        authentication_provider: AuthenticationProvider,
        parse_node_factory: ParseNodeFactory = ParseNodeFactoryRegistry(),
        serialization_writer_factory:
        SerializationWriterFactory = SerializationWriterFactoryRegistry(),
        http_client: httpx.AsyncClient = KiotaClientFactory.create_with_default_middleware()
    ) -> None:

        if not authentication_provider:
            raise TypeError("Authentication provider cannot be null")
        self._authentication_provider = authentication_provider
        if not parse_node_factory:
            raise TypeError("Parse node factory cannot be null")
        self._parse_node_factory = parse_node_factory
        if not serialization_writer_factory:
            raise TypeError("Serialization writer factory cannot be null")
        self._serialization_writer_factory = serialization_writer_factory
        if not http_client:
            raise TypeError("Http Client cannot be null")

        self._http_client = http_client

        self._base_url: str = ''

    @property
    def base_url(self) -> str:
        """Gets the base url for every request

        Returns:
            str: The base url
        """
        return self._base_url

    @base_url.setter
    def base_url(self, value: str) -> None:
        """Sets the base url for every request

        Args:
            value (str): The new base url
        """
        if value:
            self._base_url = value

    def get_serialization_writer_factory(self) -> SerializationWriterFactory:
        """Gets the serialization writer factory currently in use for the HTTP core service.
        Returns:
            SerializationWriterFactory: the serialization writer factory currently in use for the
            HTTP core service.
        """
        return self._serialization_writer_factory

    def get_response_content_type(self, response: httpx.Response) -> Optional[str]:
        header = response.headers.get("content-type")
        if not header:
            return None
        segments = header.lower().split(';')
        if not segments:
            return None
        return segments[0]

    async def send_async(
        self, request_info: RequestInformation, model_type: ParsableFactory,
        error_map: Dict[str, ParsableFactory]
    ) -> Optional[ModelType]:
        """Excutes the HTTP request specified by the given RequestInformation and returns the
        deserialized response model.
        Args:
            request_info (RequestInformation): the request info to execute.
            type (ParsableFactory): the class of the response model to deserialize the response into
            error_map (Dict[str, ParsableFactory]): the error dict to use in
            case of a failed request.

        Returns:
            ModelType: the deserialized response model.
        """
        if not request_info:
            raise TypeError("Request info cannot be null")

        response = await self.get_http_response_message(request_info)

        response_handler = self.get_response_handler(request_info)
        if response_handler:
            return await response_handler.handle_response_async(response)

        await self.throw_failed_responses(response, error_map)
        if self._should_return_none(response):
            return None
        root_node = await self.get_root_parse_node(response)
        result = root_node.get_object_value(model_type)
        return result

    async def send_collection_async(
        self, request_info: RequestInformation, model_type: ParsableFactory,
        error_map: Dict[str, ParsableFactory]
    ) -> Optional[List[ModelType]]:
        """Excutes the HTTP request specified by the given RequestInformation and returns the
        deserialized response model collection.
        Args:
            request_info (RequestInformation): the request info to execute.
            type (ParsableFactory): the class of the response model to deserialize the response into
            error_map (Dict[str, ParsableFactory]): the error dict to use in
            case of a failed request.

        Returns:
            ModelType: the deserialized response model collection.
        """
        if not request_info:
            raise TypeError("Request info cannot be null")
        response = await self.get_http_response_message(request_info)

        response_handler = self.get_response_handler(request_info)
        if response_handler:
            return await response_handler.handle_response_async(response)

        await self.throw_failed_responses(response, error_map)
        if self._should_return_none(response):
            return None
        root_node = await self.get_root_parse_node(response)
        result = root_node.get_collection_of_object_values(model_type)
        return result

    async def send_collection_of_primitive_async(
        self, request_info: RequestInformation, response_type: ResponseType,
        error_map: Dict[str, ParsableFactory]
    ) -> Optional[List[ResponseType]]:
        """Excutes the HTTP request specified by the given RequestInformation and returns the
        deserialized response model collection.
        Args:
            request_info (RequestInformation): the request info to execute.
            response_type (ResponseType): the class of the response model to deserialize the
            response into.
            error_map (Dict[str, ParsableFactory]): the error dict to use in
            case of a failed request.

        Returns:
            Optional[List[ModelType]]: he deserialized response model collection.
        """
        if not request_info:
            raise TypeError("Request info cannot be null")

        response = await self.get_http_response_message(request_info)

        response_handler = self.get_response_handler(request_info)
        if response_handler:
            return await response_handler.handle_response_async(response)

        await self.throw_failed_responses(response, error_map)
        if self._should_return_none(response):
            return None
        root_node = await self.get_root_parse_node(response)
        return root_node.get_collection_of_primitive_values(response_type)

    async def send_primitive_async(
        self, request_info: RequestInformation, response_type: ResponseType,
        error_map: Dict[str, ParsableFactory]
    ) -> Optional[ResponseType]:
        """Excutes the HTTP request specified by the given RequestInformation and returns the
        deserialized primitive response model.
        Args:
            request_info (RequestInformation): the request info to execute.
            response_type (ResponseType): the class of the response model to deserialize the
            response into.
            error_map (Dict[str, ParsableFactory]): the error dict to use in case
            of a failed request.

        Returns:
            ResponseType: the deserialized primitive response model.
        """
        if not request_info:
            raise TypeError("Request info cannot be null")

        response = await self.get_http_response_message(request_info)

        response_handler = self.get_response_handler(request_info)
        if response_handler:
            return await response_handler.handle_response_async(response)

        await self.throw_failed_responses(response, error_map)
        if self._should_return_none(response):
            return None
        root_node = await self.get_root_parse_node(response)
        if response_type == str:
            return root_node.get_string_value()
        if response_type == int:
            return root_node.get_int_value()
        if response_type == float:
            return root_node.get_float_value()
        if response_type == bool:
            return root_node.get_boolean_value()
        if response_type == datetime:
            return root_node.get_datetime_value()
        if response_type == bytes:
            return root_node.get_bytearray_value()
        raise Exception("Found unexpected type to deserialize")

    async def send_no_response_content_async(
        self, request_info: RequestInformation, error_map: Dict[str, ParsableFactory]
    ) -> None:
        """Excutes the HTTP request specified by the given RequestInformation and returns the
        deserialized primitive response model.
        Args:
            request_info (RequestInformation):the request info to execute.
            error_map (Dict[str, ParsableFactory]): the error dict to use in case
            of a failed request.
        """
        if not request_info:
            raise TypeError("Request info cannot be null")

        response = await self.get_http_response_message(request_info)

        response_handler = self.get_response_handler(request_info)
        if response_handler:
            return await response_handler.handle_response_async(response)

        await self.throw_failed_responses(response, error_map)

    def enable_backing_store(self, backing_store_factory: Optional[BackingStoreFactory]) -> None:
        """Enables the backing store proxies for the SerializationWriters and ParseNodes in use.
        Args:
            backing_store_factory (Optional[BackingStoreFactory]): the backing store factory to use.
        """
        self._parse_node_factory = enable_backing_store_for_parse_node_factory(
            self._parse_node_factory
        )
        self._serialization_writer_factory = enable_backing_store_for_serialization_writer_factory(
            self._serialization_writer_factory
        )
        if not (self._serialization_writer_factory or self._parse_node_factory):
            raise Exception("Unable to enable backing store")
        if backing_store_factory:
            BackingStoreFactorySingleton.__instance = backing_store_factory

    async def get_root_parse_node(self, response: httpx.Response) -> ParseNode:
        payload = response.content
        response_content_type = self.get_response_content_type(response)
        if not response_content_type:
            raise Exception("No response content type found for deserialization")

        return self._parse_node_factory.get_root_parse_node(response_content_type, payload)

    def _should_return_none(self, response: httpx.Response) -> bool:
        return response.status_code == 204

    async def throw_failed_responses(
        self, response: httpx.Response, error_map: Dict[str, ParsableFactory]
    ) -> None:
        if response.is_success:
            return

        status_code = response.status_code
        status_code_str = str(response.status_code)

        if not error_map:
            raise APIError(
                "The server returned an unexpected status code and no error class is registered"
                f" for this code {status_code}"
            )
        if (status_code_str not in error_map) and (
            (400 <= status_code < 500 and '4XX' not in error_map) or
            (500 <= status_code < 600 and '5XX' not in error_map)
        ):
            raise APIError(
                "The server returned an unexpected status code and no error class is registered"
                f" for this code {status_code}"
            )

        error_class = None
        if status_code_str in error_map:
            error_class = error_map[status_code_str]
        elif 400 <= status_code < 500:
            error_class = error_map['4XX']
        elif 500 <= status_code < 600:
            error_class = error_map['5XX']

        root_node = await self.get_root_parse_node(response)
        error = root_node.get_object_value(error_class)

        if error:
            raise error
        raise APIError(f"Unexpected error type: {type(error)}")

    async def get_http_response_message(self, request_info: RequestInformation) -> httpx.Response:
        self.set_base_url_for_request_information(request_info)
        await self._authentication_provider.authenticate_request(request_info)

        request = self.get_request_from_request_information(request_info)

        # Pass request options in the headers as send method does not support.
        # The header will be removed by the last middleware before the request is sent.
        request.headers["request_options"] = str(request_info.request_options)

        resp = await self._http_client.send(request)
        return resp

    def get_response_handler(self, request_info: RequestInformation) -> Any:
        response_handler_option = request_info.request_options.get(
            ResponseHandlerOption().get_key()
        )
        if response_handler_option:
            return response_handler_option.response_handler
        return None

    def set_base_url_for_request_information(self, request_info: RequestInformation) -> None:
        request_info.path_parameters["baseurl"] = self.base_url

    def get_request_from_request_information(
        self, request_info: RequestInformation
    ) -> httpx.Request:
        request = self._http_client.build_request(
            method=request_info.http_method.value,
            url=request_info.url,
            headers=request_info.request_headers,
            content=request_info.content,
        )
        return request
