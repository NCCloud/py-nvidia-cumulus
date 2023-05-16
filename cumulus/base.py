import json
from requests import Session, Response


class RequestError(Exception):
    """
    Custom request error representation
    """

    def __init__(self, response: Response) -> None:
        try:
            self.message = (
                "The request for URL {} "
                "failed with code {} {}: {}".format(
                    response.url, response.status_code,
                    response.reason, response.json()
                )
            )
        except Exception:
            self.message = (
                "The request for URL {} failed with code {} {} "
                "without additional information.".format(
                    response.url, response.status_code, response.reason
                )
            )

        super().__init__(self.message)
        self.response = response
        self.request_body = response.request.body
        self.url = response.url
        self.error = response.text

    def __str__(self):
        return self.message


class InvalidData(Exception):

    def __init__(self, response: Response) -> None:
        self.url = response.url
        self.response = response
        self.request_body = response.request.body
        self.error = response.text

        self.message = f"The URL {self.url} returned non json data"

        super().__init__(self.message)


class Request:
    """
    Construct a request to the Cumulus API endpoint

    :param str url: A URL to the Cumulus host
    :param requests.Session http_session: A session to make requests
    """

    def __init__(self, url: str, http_session: Session) -> None:
        self.url = url
        self.http_session = http_session

    def _send_request(self,
                      method: str,
                      data: dict = {},
                      params: dict = {}) -> dict:
        """
        Send a request to the API server
        :raises RequestError: if response status is >=400
        """
        headers = {'Content-Type': 'application/json'}

        response = self.http_session.request(
            method=method,
            url=self.url,
            json=data,
            params=params,
            headers=headers
        )
        if not response.ok:
            raise RequestError(response)

        try:
            return response.json()
        except json.JSONDecodeError:
            raise InvalidData(response)

    def get(self, params: dict = {}) -> dict:
        """
        Make a GET request
        """
        return self._send_request(method="get", params=params)

    def post(self, data: dict = {}, params: dict = {}):
        """
        Make a POST request
        """
        return self._send_request(method="post", data=data, params=params)

    def patch(self, data: dict = {}, params: dict = {}):
        """
        Make a PATCH request
        """
        return self._send_request(method="patch", data=data, params=params)

    def delete(self, params: dict = {}):
        """
        Make a DELETE request
        """
        return self._send_request(method="delete", params=params)
