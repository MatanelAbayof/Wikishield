import time
from abc import ABC

import requests
from requests import ConnectionError


class BaseApi(ABC):
    """
    this is a generic class with helpful functions for API 
    """

    _MAX_TRIES = 10
    _TIMEOUT = 40
    _SLEEP_COEFFICIENT = 5

    def __init__(self):
        """
        initialize the class
        """

        pass

    @property
    def api_path(self) -> str:
        """
        get API URL path
        """

        raise NotImplementedError('`api_path` method should be implement in subclass')

    def fetch_json(self, params):
        """
        fetch JSON from API with GET method

        this fetch method has ability to recover from: 429 status - "Too Many Requests" (`See here <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429>`) by using many tries and sleep

        the request has timeout of 10 seconds

        param params: list of parameters to send

        return JSON result
        """

        tries = 0
        while tries < self._MAX_TRIES:
            try:
                return requests.get(self.api_path, params=params, timeout=self._TIMEOUT).json()
            except:
                tries += 1
                print("I am sleep with try = {}".format(tries))
                sleep_time = tries * self._SLEEP_COEFFICIENT
                time.sleep(sleep_time)

        raise ConnectionError("Cannot connect to {0} with params = {1}".format(self.api_path, params))
