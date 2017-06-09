"""
Module for the SQL API

.. module:: carto.sql
   :platform: Unix, Windows
   :synopsis: Module for the SQL API

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from .exceptions import CartoException

SQL_API_URL = 'api/{api_version}/sql'
SQL_BATCH_API_URL = 'api/{api_version}/sql/job/'

MAX_GET_QUERY_LEN = 1024


class SQLClient(object):
    """
    Allows you to send requests to CARTO's SQL API
    """
    def __init__(self, auth_client, api_version='v2'):
        """
        :param auth_client: Auth client to make authorized requests, such as
                            APIKeyAuthClient
        :param api_version: Current version is 'v2'. 'v1' can be used to avoid
                            caching, but it's not guaranteed to work
        :type auth_client: :class:`carto.auth.APIKeyAuthClient`
        :type api_version: str

        :return:
        """
        self.auth_client = auth_client
        self.api_url = SQL_API_URL.format(api_version=api_version)

        self.api_key = getattr(self.auth_client, 'api_key', None)
        self.username = getattr(self.auth_client, 'username', None)
        self.base_url = self.auth_client.base_url

    def send(self, sql, parse_json=True, do_post=True, format=None):
        """
        Executes SQL query in a CARTO server

        :param sql: The SQL
        :param parse_json: Set it to False if you want raw reponse
        :param do_post: Set it to True to force post request
        :param format: Any of the data export formats allowed by CARTO's
                        SQL API
        :type sql: str
        :type parse_json: boolean
        :type do_post: boolean
        :type format: str

        :return: response data, either as json or as a regular
                    response.content object
        :rtype: object

        :raise: CartoException
        """
        try:
            params = {'q': sql}
            if format:
                params['format'] = format
                if format not in ['json', 'geojson']:
                    parse_json = False

            if len(sql) < MAX_GET_QUERY_LEN and do_post is False:
                resp = self.auth_client.send(self.api_url,
                                             'GET',
                                             params=params)
            else:
                resp = self.auth_client.send(self.api_url, 'POST', data=params)

            return self.auth_client.get_response_data(resp, parse_json)
        except Exception as e:
            raise CartoException(e)


class BatchSQLClient(object):
    """
    Allows you to send requests to CARTO's Batch SQL API
    """
    def __init__(self, client, api_version='v2'):
        """
        :param client: Auth client to make authorized requests, such as
                        APIKeyAuthClient
        :param api_version: Current version is 'v2'. 'v1' can be used to avoid
                            caching, but it's not guaranteed to work
        :type auth_client: :class:`carto.auth.APIKeyAuthClient`
        :type api_version: str

        :return:
        """
        self.client = client
        self.api_url = SQL_BATCH_API_URL.format(api_version=api_version)
        self.api_key = self.client.api_key \
            if hasattr(self.client, "api_key") else None

    def update_from_dict(self, data_dict):
        """
        :param data_dict: Dictionary to be mapped into object attributes
        :type data_dict: dict

        :return:
        """
        for k, v in data_dict.items():
            setattr(self, k, v)
        if "item_queue_id" in data_dict:
            self.id = data_dict["item_queue_id"]

    def send(self, url, http_method, json_body=None, http_header=None):
        """
        Executes Batch SQL query in a CARTO server

        :param url: Endpoint url
        :param http_method: The method used to make the request to the API
        :param json_body: The information that needs to be sent, by default
                            is set to None
        :param http_header: The header used to make write requests to the API,
                            by default is none
        :type url: str
        :type http_method: str
        :type json_body: dict
        :type http_header: str

        :return: Response data, either as json or as a regular response.content
                object
        :rtype: object

        :raise: CartoException
        """
        try:
            data = self.client.send(url,
                                    http_method=http_method,
                                    headers=http_header,
                                    json=json_body)
            data_json = self.client.get_response_data(data)
        except Exception as e:
            raise CartoException(e)
        return data_json

    def create(self, sql_query):
        """
        Creates a new batch SQL query.

        Batch SQL jobs are asynchronous, once created you should call
        :func:`carto.sql.BatchSQLClient.read` method given the `job_id`
        to retrieve the state of the batch query

        :param sql_query: The SQL query to be used
        :type sql_query: str or list of str

        :return: Response data, either as json or as a regular response.content
                    object
        :rtype: object

        :raise: CartoException
        """
        header = {'content-type': 'application/json'}
        data = self.send(self.api_url,
                         http_method="POST",
                         json_body={"query": sql_query},
                         http_header=header)
        return data

    def read(self, job_id):
        """
        Reads the information for a specific Batch API request

        :param job_id: The id of the job to be read from
        :type job_id: str

        :return: Response data, either as json or as a regular response.content
                    object
        :rtype: object

        :raise: CartoException
        """
        data = self.send(self.api_url + job_id, http_method="GET")
        return data

    def update(self, job_id, sql_query):
        """
        Updates the sql query of a specific job

        :param job_id: The id of the job to be updated
        :param sql_query: The new SQL query for the job
        :type job_id: str
        :type sql_query: str

        :return: Response data, either as json or as a regular response.content
                    object
        :rtype: object

        :raise: CartoException
        """
        header = {'content-type': 'application/json'}
        data = self.send(self.api_url + job_id,
                         http_method="PUT",
                         json_body={"query": sql_query},
                         http_header=header)
        return data

    def cancel(self, job_id):
        """
        Cancels a job

        :param job_id: The id of the job to be cancelled
        :type job_id: str

        :return: A status code depending on whether the cancel request was
                    successful
        :rtype: str

        :raise CartoException:
        """
        confirmation = self.send(self.api_url + job_id, http_method="DELETE")
        return confirmation['status']
