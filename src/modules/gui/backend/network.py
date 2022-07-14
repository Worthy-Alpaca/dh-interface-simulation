import requests
import json
from typing import Union


class NetworkRequests:
    def __init__(self, networkAddress: str, basePath: str) -> None:
        """Class for API requests.

        Args:
            networkAddress (str): The network address of the API.
            basePath (str): The base path to the API.
        """

        try:
            request = requests.get(networkAddress + "/")
            request = request.json()
            basepath = request["Basepath"]
        except:
            basepath = basePath
        self.networkAddress = networkAddress + basepath

    def get(
        self, endpoint: str, params: dict = {}
    ) -> Union[tuple[bool, Exception], dict]:
        """Function for HTTP GET call.

        Args:
            endpoint (str): The current endpoint.
            params (dict, optional): The request parameters. Defaults to {}.

        Returns:
            Union[tuple[bool, Exception], dict]: The returned data.
        """
        queryParams = "?"
        for key in params:
            queryParams = queryParams + f"{key}={params[key]}&"

        try:
            request = requests.get(self.networkAddress + endpoint + queryParams)
        except Exception as e:
            return (False, e)

        return request.json()

    def put(
        self, endpoint: str, params: dict, data: dict
    ) -> Union[tuple[bool, Exception], dict]:
        """Function for HTTP PUT call.

        Args:
            endpoint (str): The current endpoint.
            params (dict): The request parameters.
            data (dict): The request data.

        Returns:
            Union[tuple[bool, Exception], dict]: The returned data.
        """
        queryParams = "?"
        for key in params:
            queryParams = queryParams + f"{key}={params[key]}&"

        try:
            request = requests.put(
                self.networkAddress + endpoint + queryParams, data=json.dumps(data)
            )
        except Exception as e:
            return (False, e)

        return request
