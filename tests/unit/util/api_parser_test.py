from datetime import timedelta
from json import dumps
from typing import Union

from mock import MagicMock, patch

from requests import ConnectionError

from util import api

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



class TestApiParser:

    def test_when_api_returns_success(self):
        """
        This scenario emulates when the API returns status_code=200 and its content
        :return:
        """

        expected_content = {"key1": "value1"}
        @api(host="any_host", endpoint="any_endpoint")
        def mocked_func(*_, **__):
            return MockResponse(
                status=200,
                content=expected_content
            )

        response: MockResponse = mocked_func("any_url")

        assert response["success"]
        assert response["metadata"]["status_code"] == 200
        assert response["data"] == expected_content

    def test_when_api_returns_error(self):
        """
        This scenario emulates when the API returned status code=400 (error)
        """

        @api(host="any_host", endpoint="any_endpoint")
        def mocked_func(*_, **__):
            return MockResponse(
                status=400,
                content="Unknown error"
            )

        response = mocked_func("any_url")
        assert response == {'success': False, 'metadata': {'endpoint': 'any_endpoint', 'error': 'Unknown error'}}

    def test_when_api_fails_communication(self):
        """
        This scenario emulates a ConnectionError exception
        """

        @api(host="any_host", endpoint="any_endpoint")
        def mocked_func(*_, **__):
            raise ConnectionError("Mocked exception")

        response = mocked_func("any_url")
        assert response == {'success': False, 'metadata': {'endpoint': 'any_endpoint', 'error': 'ConnectionError: Mocked exception'}}
