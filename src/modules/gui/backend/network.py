import requests
import json


class NetworkRequests:
    def __init__(self, networkAddress: str, basePath: str) -> None:
        self.networkAddress = networkAddress + basePath

    def get(self, endpoint: str, params: dict = {}) -> (tuple[bool, Exception] | dict):
        queryParams = "?"
        for key in params:
            queryParams = queryParams + f"{key}={params[key]}&"

        try:
            request = requests.get(self.networkAddress + endpoint + queryParams)
        except Exception as e:
            return (False, e)

        return request.json()

    def put(self, endpoint: str, params: dict, data: dict):
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
