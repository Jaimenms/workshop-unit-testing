from datetime import timedelta
from json import dumps
from typing import Union

from mock import MagicMock, patch

import api

BASE_URL = "http://api.citybik.es/v2/networks"
EXPECTED_NETWORKS_URL = f"{BASE_URL}?fields=id,location.country"
EXPECTED_BY_ID = "foobar"
EXPECTED_NETWORK_URL = f"{BASE_URL}/{EXPECTED_BY_ID}"


class MockResponse:

    def __init__(self,
                 status: int,
                 content: Union[dict, str] = None):
        self.status_code = status
        self.ok = 200 <= status < 300
        self.elapsed = timedelta(seconds=1)

        if isinstance(content, dict):
            self.text = dumps(content)
        else:
            self.text = content


def mock_requests_exception(*_, **__):
    raise ConnectionError("Mocked exception")


class TestCityBikes:

    def setup_method(self):
        self.api = api.CityBikes()

    @patch("requests.get", return_value=MockResponse(
        status=200,
        content={
            "networks": [
                {
                    "id": "hello-world"
                },
                {
                    "id": "foo-bar"
                }
            ]
        }
    ))
    def test_networks_endpoint_returns_expected_content_for_success(self,
                                                                    get_patch: MagicMock):
        response = self.api.networks()

        get_patch.assert_called_once()
        assert response == {
            "data": {
                "networks": [
                    {
                        "id": "hello-world"
                    },
                    {
                        "id": "foo-bar"
                    }
                ]
            },
            "success": True,
            "metadata": {
                "endpoint": "v2/networks?fields=id,location.country",
                "elapsed_time": 1000.0,
                "status_code": 200
            }
        }

    @patch("requests.get", return_value=MockResponse(
        status=200,
        content=None
    ))
    def test_networks_endpoint_validate_requested_url(self,
                                                      get_patch: MagicMock):
        self.api.networks()
        assert "url" in list(get_patch.call_args.kwargs.keys())
        assert EXPECTED_NETWORKS_URL == get_patch.call_args.kwargs["url"]

    @patch("requests.get", return_value=MockResponse(
        status=200,
        content=None
    ))
    def test_network_endpoint_validate_requested_url(self,
                                                      get_patch: MagicMock):
        self.api.network(by_id=EXPECTED_BY_ID)
        assert "url" in list(get_patch.call_args.kwargs.keys())
        assert EXPECTED_NETWORK_URL == get_patch.call_args.kwargs["url"]

    @patch("requests.get", return_value=MockResponse(
        status=400,
        content="Unknown error"
    ))
    def test_networks_endpoint_returns_expected_content_for_failure(self,
                                                                    get_patch: MagicMock):
        response = self.api.networks()

        get_patch.assert_called_once()
        assert response == {
            "success": False,
            "metadata": {
                "endpoint": "v2/networks?fields=id,location.country",
                "error": "Unknown error"
            }
        }

    @patch("requests.get", mock_requests_exception)
    def test_networks_endpoint_returns_expected_content_for_exception(self):
        response = self.api.networks()
        assert response == {
            "success": False,
            "metadata": {
                "endpoint": "v2/networks?fields=id,location.country",
                "error": "ConnectionError: Mocked exception"
            }
        }

    @patch("requests.get", return_value=MockResponse(
        status=200,
        content={
            "network": {
                "id": "foobar"
            }
        }
    ))
    def test_network_endpoint_returns_expected_content_for_success(self,
                                                                   get_patch: MagicMock):
        response = self.api.network(by_id="foobar")

        get_patch.assert_called_once()
        assert response == {
            "data": {
                "network": {
                    "id": "foobar"
                }
            },
            "success": True,
            "metadata": {
                "endpoint": "v2/networks/{network_id}",
                "elapsed_time": 1000.0,
                "status_code": 200
            }
        }

    @patch("requests.get", return_value=MockResponse(
        status=400,
        content="Unknown error"
    ))
    def test_network_endpoint_returns_expected_content_for_failure(self,
                                                                   get_patch: MagicMock):
        response = self.api.network(by_id="foobar")

        get_patch.assert_called_once()
        assert response == {
            "success": False,
            "metadata": {
                "endpoint": "v2/networks/{network_id}",
                "error": "Unknown error"
            }
        }

    @patch("requests.get", mock_requests_exception)
    def test_network_endpoint_returns_expected_content_for_exception(self):
        response = self.api.network(by_id="foobar")
        assert response == {
            "success": False,
            "metadata": {
                "endpoint": "v2/networks/{network_id}",
                "error": "ConnectionError: Mocked exception"
            }
        }
