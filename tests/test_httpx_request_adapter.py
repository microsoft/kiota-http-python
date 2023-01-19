import httpx
import pytest
from asyncmock import AsyncMock
from kiota_abstractions.api_error import APIError
from kiota_abstractions.method import Method
from kiota_abstractions.native_response_handler import NativeResponseHandler
from kiota_abstractions.serialization import (
    ParseNodeFactoryRegistry,
    SerializationWriterFactoryRegistry,
)

from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from kiota_http.middleware.options import ResponseHandlerOption

from .helpers import MockResponseObject

BASE_URL = "https://graph.microsoft.com"


def test_create_request_adapter(auth_provider):
    request_adapter = HttpxRequestAdapter(auth_provider)
    assert request_adapter._authentication_provider is auth_provider
    assert isinstance(request_adapter._parse_node_factory, ParseNodeFactoryRegistry)
    assert isinstance(
        request_adapter._serialization_writer_factory, SerializationWriterFactoryRegistry
    )
    assert isinstance(request_adapter._http_client, httpx.AsyncClient)
    assert request_adapter.base_url == ''


def test_create_request_adapter_no_auth_provider():
    with pytest.raises(TypeError):
        HttpxRequestAdapter(None)


def test_set_base_url(auth_provider):
    request_adapter = HttpxRequestAdapter(auth_provider)
    assert request_adapter.base_url == ''
    request_adapter.base_url = BASE_URL
    assert request_adapter.base_url == BASE_URL


def test_get_serialization_writer_factory(request_adapter):
    assert isinstance(
        request_adapter.get_serialization_writer_factory(), SerializationWriterFactoryRegistry
    )


def test_get_response_content_type(request_adapter, simple_response):
    content_type = request_adapter.get_response_content_type(simple_response)
    assert content_type == 'application/json'


def test_set_base_url_for_request_information(request_adapter, request_info):
    request_adapter.base_url = BASE_URL
    request_adapter.set_base_url_for_request_information(request_info)
    assert request_info.path_parameters["baseurl"] == BASE_URL


def test_get_request_from_request_information(request_adapter, request_info):
    request_info.http_method = Method.GET
    request_info.url = BASE_URL
    request_info.content = bytes('hello world', 'utf_8')
    req = request_adapter.get_request_from_request_information(request_info)
    assert isinstance(req, httpx.Request)


def test_get_response_handler(request_adapter, request_info):
    response_handler_option = ResponseHandlerOption(response_handler=NativeResponseHandler())

    request_info.http_method = Method.GET
    request_info.url = BASE_URL
    request_info.content = bytes('hello world', 'utf_8')
    request_info.add_request_options([response_handler_option])
    response_handler = request_adapter.get_response_handler(request_info)
    assert isinstance(response_handler, NativeResponseHandler)


def test_enable_backing_store(request_adapter):
    request_adapter.enable_backing_store(None)
    assert request_adapter._parse_node_factory
    assert request_adapter._serialization_writer_factory


@pytest.mark.asyncio
async def test_get_root_parse_node(request_adapter, simple_response):
    assert simple_response.text == '{"error": "not found"}'
    assert simple_response.status_code == 404
    content_type = request_adapter.get_response_content_type(simple_response)
    assert content_type == 'application/json'

    with pytest.raises(Exception) as e:
        await request_adapter.get_root_parse_node(simple_response)


@pytest.mark.asyncio
async def test_throw_failed_responses_null_error_map(request_adapter, simple_response):
    assert simple_response.text == '{"error": "not found"}'
    assert simple_response.status_code == 404
    content_type = request_adapter.get_response_content_type(simple_response)
    assert content_type == 'application/json'

    with pytest.raises(
        APIError,
        match=
        r"The server returned an unexpected status code and"\
            " no error class is registered for this code 404"
    ):
        await request_adapter.throw_failed_responses(simple_response, None)


@pytest.mark.asyncio
async def test_throw_failed_responses_no_error_class(
    request_adapter, simple_response, mock_error_map
):
    assert simple_response.text == '{"error": "not found"}'
    assert simple_response.status_code == 404
    content_type = request_adapter.get_response_content_type(simple_response)
    assert content_type == 'application/json'

    with pytest.raises(
        APIError,
        match=
        r"The server returned an unexpected status code and"\
        " no error class is registered for this code 404"
    ):
        await request_adapter.throw_failed_responses(simple_response, mock_error_map)


@pytest.mark.asyncio
async def test_throw_failed_responses_status_code_str_in_error_map(
    request_adapter, mock_error_map, mock_error_object
):
    request_adapter.get_root_parse_node = AsyncMock(return_value=mock_error_object)
    resp = httpx.Response(status_code=500, headers={"Content-Type": "application/json"})
    assert resp.status_code == 500
    content_type = request_adapter.get_response_content_type(resp)
    assert content_type == 'application/json'

    with pytest.raises(Exception, match=r"Internal Server Error"):
        await request_adapter.throw_failed_responses(resp, mock_error_map)


@pytest.mark.asyncio
async def test_send_async(request_adapter, request_info, mock_user_response, mock_user):
    request_adapter.get_http_response_message = AsyncMock(return_value=mock_user_response)
    request_adapter.get_root_parse_node = AsyncMock(return_value=mock_user)
    resp = await request_adapter.get_http_response_message(request_info)
    assert resp.headers.get("content-type") == 'application/json'
    final_result = await request_adapter.send_async(request_info, MockResponseObject, {})
    assert final_result.display_name == mock_user.display_name
    assert final_result.office_location == mock_user.office_location
    assert final_result.business_phones == mock_user.business_phones
    assert final_result.age == mock_user.age
    assert final_result.gpa == mock_user.gpa
    assert final_result.is_active == mock_user.is_active
    assert final_result.mobile_phone == mock_user.mobile_phone


@pytest.mark.asyncio
async def test_send_collection_async(request_adapter, request_info, mock_users_response, mock_user):
    request_adapter.get_http_response_message = AsyncMock(return_value=mock_users_response)
    request_adapter.get_root_parse_node = AsyncMock(return_value=mock_user)
    resp = await request_adapter.get_http_response_message(request_info)
    assert resp.headers.get("content-type") == 'application/json'
    final_result = await request_adapter.send_collection_async(request_info, MockResponseObject, {})
    assert final_result[0].display_name == mock_user.display_name
    assert final_result[1].office_location == mock_user.office_location
    assert final_result[0].business_phones == mock_user.business_phones
    assert final_result[1].age == mock_user.age
    assert final_result[1].gpa == mock_user.gpa
    assert final_result[0].is_active == mock_user.is_active
    assert final_result[1].mobile_phone == mock_user.mobile_phone


@pytest.mark.asyncio
async def test_send_collection_of_primitive_async(
    request_adapter, request_info, mock_primitive_collection_response, mock_primitive
):
    request_adapter.get_http_response_message = AsyncMock(
        return_value=mock_primitive_collection_response
    )
    request_adapter.get_root_parse_node = AsyncMock(return_value=mock_primitive)
    resp = await request_adapter.get_http_response_message(request_info)
    assert resp.headers.get("content-type") == 'application/json'
    final_result = await request_adapter.send_collection_of_primitive_async(request_info, float, {})
    assert final_result == [12.1, 12.2, 12.3, 12.4, 12.5]


@pytest.mark.asyncio
async def test_send_primitive_async(
    request_adapter, request_info, mock_primitive_response, mock_primitive
):
    request_adapter.get_http_response_message = AsyncMock(return_value=mock_primitive_response)
    request_adapter.get_root_parse_node = AsyncMock(return_value=mock_primitive)
    resp = await request_adapter.get_http_response_message(request_info)
    assert resp.headers.get("content-type") == 'application/json'
    final_result = await request_adapter.send_primitive_async(request_info, float, {})
    assert final_result == 22.3


@pytest.mark.asyncio
async def test_send_primitive_async_no_content(
    request_adapter, request_info, mock_no_content_response
):
    request_adapter.get_http_response_message = AsyncMock(return_value=mock_no_content_response)
    resp = await request_adapter.get_http_response_message(request_info)
    assert resp.headers.get("content-type") == 'application/json'
    final_result = await request_adapter.send_primitive_async(request_info, float, {})
    assert final_result is None
