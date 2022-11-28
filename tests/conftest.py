from dataclasses import dataclass

import httpx
import pytest
from asyncmock import AsyncMock
from kiota_abstractions.authentication import AnonymousAuthenticationProvider
from kiota_abstractions.request_information import RequestInformation

from kiota_http.httpx_request_adapter import HttpxRequestAdapter

from .helpers import MockErrorObject, MockResponseObject, OfficeLocation


@pytest.fixture
def auth_provider():
    return AnonymousAuthenticationProvider()


@pytest.fixture
def request_info():
    return RequestInformation()


@pytest.fixture
def request_info_mock():
    return RequestInformation()


@pytest.fixture
def request_adapter(auth_provider):
    adapter = HttpxRequestAdapter(auth_provider)
    return adapter


@pytest.fixture
def mock_error_object():
    return MockErrorObject


@pytest.fixture
def mock_error_map():
    return {
        "500": Exception("Internal Server Error"),
    }


@pytest.fixture
def mock_request_adapter():
    resp = httpx.Response(
        json={'error': 'not found'}, status_code=404, headers={"Content-Type": "application/json"}
    )
    mock_request_adapter = AsyncMock
    mock_request_adapter.get_http_response_message = AsyncMock(return_value=resp)


@pytest.fixture
def simple_response():
    return httpx.Response(
        json={'error': 'not found'}, status_code=404, headers={"Content-Type": "application/json"}
    )


@pytest.fixture
def mock_user_response(mocker):
    return httpx.Response(
        200,
        headers={"Content-Type": "application/json"},
        json={
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
            "businessPhones": ["+1 205 555 0108"],
            "displayName": "Diego Siciliani",
            "mobilePhone": None,
            "officeLocation": "dunhill",
            "updatedAt": "2021 -07-29T03:07:25Z",
            "birthday": "2000-09-04",
            "isActive": True,
            "age": 21,
            "gpa": 3.2,
            "id": "8f841f30-e6e3-439a-a812-ebd369559c36"
        },
    )


@pytest.fixture
def mock_user(mocker):
    user = MockResponseObject()
    user.display_name == "Diego Siciliani"
    user.office_location == OfficeLocation.Dunhill
    user.business_phones == ["+1 205 555 0108"]
    user.age == 21
    user.gpa == 3.2
    user.is_active is True
    user.mobile_phone is None
    return user


@pytest.fixture
def mock_users_response(mocker):
    return httpx.Response(
        200,
        json=[
            {
                "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
                "businessPhones": ["+1 425 555 0109"],
                "displayName": "Adele Vance",
                "mobilePhone": None,
                "officeLocation": "dunhill",
                "updatedAt": "2017 -07-29T03:07:25Z",
                "birthday": "2000-09-04",
                "isActive": True,
                "age": 21,
                "gpa": 3.7,
                "id": "76cabd60-f9aa-4d23-8958-64f5539b826a"
            },
            {
                "businessPhones": ["425-555-0100"],
                "displayName": "MOD Administrator",
                "mobilePhone": None,
                "officeLocation": "oval",
                "updatedAt": "2020 -07-29T03:07:25Z",
                "birthday": "1990-09-04",
                "isActive": True,
                "age": 32,
                "gpa": 3.9,
                "id": "f58411c7-ae78-4d3c-bb0d-3f24d948de41"
            },
        ],
    )


@pytest.fixture
def mock_primitive_collection_response(mocker):
    return httpx.Response(
        200, json=[12.1, 12.2, 12.3, 12.4, 12.5], headers={"Content-Type": "application/json"}
    )


@pytest.fixture
def mock_primitive(mocker):
    resp = MockResponseObject()
    return resp


@pytest.fixture
def mock_primitive_response(mocker):
    return httpx.Response(200, json=22.3, headers={"Content-Type": "application/json"})


@pytest.fixture
def mock_no_content_response(mocker):
    return httpx.Response(204, json="Radom JSON", headers={"Content-Type": "application/json"})
