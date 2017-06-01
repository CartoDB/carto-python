"""
Module for getting mock requests for test methods

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

import requests_mock

from carto.exceptions import CartoException


class MockRequests(object):
    """
    This class provides mock requests for testing

    """
    def __init__(self):
        """
        Init method

        :return:
        """
        self.requests = {
          "test_sql": {
            "url": "https://mock.carto.com/api/v2/sql?q=select+%2A+from+tornados&api_key=mockmockmock",
            "text": '{ \
              "rows": [ \
                "a" \
              ], \
              "total_rows": 1, \
              "time": 1 \
            }'
          }
        }

        with requests_mock.Mocker() as m:
            for method_name in self.requests:
                self.get(method_name, m)
            self.mocker = m

    def get(self, method_name, mocker):
        """
        Returns a mock request for a given `method_name`

        :param method_name: The test method name

        :return:
            A `requests_mock` object
        :raise:
            CartoException
        """
        try:
            if method_name in self.requests:
                r = self.requests[method_name]
                mocker.get(r['url'], text=r['text'])
            else:
                raise CartoException('method_name not found: ' + method_name)
        except Exception as e:
            raise CartoException(e)


class NotMockRequests(object):
    """
    Use an instance of this class for actual integration tests

    """

    def __init__(self):
        self.mocker = self

    def get(self, method_name, mocker):
        return None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return
