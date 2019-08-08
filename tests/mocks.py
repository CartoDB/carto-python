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
            "method": "get",
            "text": '{ \
              "rows": [ \
                "a" \
              ], \
              "total_rows": 1, \
              "time": 1 \
            }'
          },
          "test_analysis_1": {
            "method": "get",
            "url": "https://mock.carto.com/api/v4/analysis/jobs?api_key=mockmockmock",
            "text": "[{},{}]"
          },
          "test_analysis_2": {
            "method": "post",
            "url": "https://mock.carto.com/api/v4/analysis/jobs",
            "text": '{"job_id":"abc"}'
          },
          "test_analysis_3": {
            "method": "get",
            "url": "https://mock.carto.com/api/v4/analysis/jobs/abc",
            "text": '{"job_id":"abc"}'
          },
          "test_analysis_4": {
            "method": "post",
            "url": "https://mock.carto.com/api/v4/analysis/jobs/abc/schedule",
            "text": '{"schedule_id":"xyz"}'
          },
          "test_analysis_5": {
            "method": "get",
            "url": "https://mock.carto.com/api/v4/analysis/jobs/abc/schedules",
            "text": '[{"schedule_id":"xyz"},{"schedule_id":"xyz"}]'
          },
          "test_analysis_6": {
            "method": "get",
            "url": "https://mock.carto.com/api/v4/analysis/jobs/abc/schedule/xyz",
            "text": '{"schedule_id":"xyz","status":"dead"}'
          },
          "test_analysis_7": {
            "method": "get",
            "url": "https://mock.carto.com/api/v4/analysis/jobs/abc/schedule/xyz/executions",
            "text": '[{},{"execution_id":"xxx"}]'
          },
          "test_analysis_8": {
            "method": "get",
            "url": "https://mock.carto.com/api/v4/analysis/jobs/abc/schedule/xyz/execution/xxx/debug",
            "text": '["log"]'
          },
          "test_analysis_9": {
            "method": "get",
            "url": "https://mock.carto.com/api/v4/analysis/jobs/abc/schedule/xyz/execution/xxx/log",
            "text": '[]'
          },
          "test_analysis_10": {
            "method": "delete",
            "url": "https://mock.carto.com/api/v4/analysis/jobs/abc/schedules",
            "text": '{"schedule_ids":[{},{}]}'
          },
          "test_analysis_11": {
            "method": "delete",
            "url": "https://mock.carto.com/api/v4/analysis/jobs/abc",
            "text": '{"stopped":2,"schedule_ids":[{},{}]}'
          }
        }

        with requests_mock.Mocker() as m:
            for method_name in self.requests:
                self.mock(method_name, m)
            self.mocker = m

    def mock(self, method_name, mocker):
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
                mocker.register_uri(r['method'], r['url'], text=r['text'])
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
