"""
Module for the SQL API

.. module:: carto.sql
   :platform: Unix, Windows
   :synopsis: Module for the SQL API

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

import zlib

from .exceptions import CartoException
from requests import HTTPError

SQL_API_URL = 'api/{api_version}/sql'
SQL_BATCH_API_URL = 'api/{api_version}/sql/job/'

MAX_GET_QUERY_LEN = 1024

# The chunk size should be a multiple of the filesystem/buffers block
# size. Big values can cause resource starvation and OTOH small values
# incur in some protocol overhead. Typical linux block size is 4 KB.
DEFAULT_CHUNK_SIZE = 8 * 1024 # 8 KB provides good results in practice

# The compression level of gzip/zlib ranges from 1 (fastest, least
# compression) to 9 (slowest, most compression).  In our performance
# tests, we determined that the most efficient way to transmit data
# end-to-end is to use compression levels 1 or 2 (compressing in the
# client, transmiting through network, decompressing and loading in
# the DB). Those levels are also gentle with platform CPU usage.
DEFAULT_COMPRESSION_LEVEL = 1


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

    def send(self, sql, parse_json=True, do_post=True, format=None, **request_args):
        """
        Executes SQL query in a CARTO server

        :param sql: The SQL
        :param parse_json: Set it to False if you want raw reponse
        :param do_post: Set it to True to force post request
        :param format: Any of the data export formats allowed by CARTO's
                        SQL API
        :param request_args: Additional parameters to send with the request
        :type sql: str
        :type parse_json: boolean
        :type do_post: boolean
        :type format: str
        :type request_args: dictionary

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

            if request_args is not None:
                for attr in request_args:
                    params[attr] = request_args[attr]

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


class CopySQLClient(object):
    """
    Allows to use the PostgreSQL COPY command for efficient streaming
    of data to and from CARTO.
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
        self.api_url = SQL_API_URL.format(api_version=api_version)
        self.api_key = self.client.api_key \
            if hasattr(self.client, "api_key") else None

    def _read_in_chunks(self, file_object, chunk_size=DEFAULT_CHUNK_SIZE):
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def _compress_chunks(self, chunk_generator, compression_level):
        for chunk in chunk_generator:
            yield zlib.compress(chunk, compression_level)


    def copyfrom(self, query, iterable_data, compress=True, compression_level=DEFAULT_COMPRESSION_LEVEL):
        """
        Gets data from an iterable object into a table

        :param query: The "COPY table_name [(column_name[, ...])]
                           FROM STDIN [WITH(option[,...])]" query to execute
        :type query: str

        :param iterable_data: An object that can be iterated
                              to retrieve the data
        :type iterable_data: object

        :return: Response data as json
        :rtype: str

        :raise CartoException:
        """

        if isinstance(iterable_data, file):
            raise CartoException('The object passed cannot be a file. Use copyfrom_file_object instead.')

        url = self.api_url + '/copyfrom'
        headers = {
            'Content-Type': 'application/octet-stream',
            'Transfer-Encoding': 'chunked'
        }
        params={'api_key': self.api_key, 'q': query}

        if compress:
            headers['Content-Encoding'] = 'gzip'
            _iterable_data = self._compress_chunks(iterable_data, compression_level)
        else:
            _iterable_data = iterable_data

        response = self.client.send(url,
                                    http_method='POST',
                                    params=params,
                                    data=_iterable_data,
                                    headers=headers,
                                    stream=True)
        response_json = self.client.get_response_data(response)

        return response_json

    def copyfrom_file_object(self, query, file_object, compress=True):
        """
        Gets data from a readable file object into a table

        :param query: The "COPY table_name [(column_name[, ...])]
                           FROM STDIN [WITH(option[,...])]" query to execute
        :type query: str

        :param file_object: A file-like object.
                            Normally the return value of open('file.ext', 'rb')
        :type file_object: file

        :return: Response data as json
        :rtype: str

        :raise CartoException:
        """

        if not isinstance(file_object, file):
            raise CartoException('The object passed is not a file')

        chunk_generator = self._read_in_chunks(file_object)
        return self.copyfrom(query, chunk_generator, compress)

    def copyfrom_file_path(self, query, path, compress=True):
        """
        Gets data from a readable file into a table

        :param query: The "COPY table_name [(column_name[, ...])]
                           FROM STDIN [WITH(option[,...])]" query to execute
        :type query: str

        :param path: A path to a file
        :type path: str

        :return: Response data as json
        :rtype: str

        :raise CartoException:
        """

        with open(path, 'rb') as f:
            result = self.copyfrom_file_object(query, f, compress)
        return result

    def copyto(self, query):
        """
        Gets data from a table into a Response object that can be iterated

        :param query: The "COPY { table_name [(column_name[, ...])] | ( query ) }
                           TO STDOUT [WITH(option[,...])]" query to execute
        :type query: str

        :return: response object
        :rtype: Response

        :raise CartoException:
        """

        url = self.api_url + '/copyto'
        params={'api_key': self.api_key, 'q': query}

        try:
            response = self.client.send(url,
                                        http_method='GET',
                                        params=params,
                                        stream=True)
            response.raise_for_status()
        except HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['error'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code, reason)
                raise CartoException(error_msg)
            else:
                raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

        return response

    def copyto_file_object(self, query, file_object):
        """
        Gets data from a table into a writable file object

        :param query: The "COPY { table_name [(column_name[, ...])] | ( query ) }
                           TO STDOUT [WITH(option[,...])]" query to execute
        :type query: str

        :param file_object: A file-like object.
                            Normally the return value of open('file.ext', 'wb')
        :type file_object: file

        :raise CartoException:
        """

        if not isinstance(file_object, file):
            raise CartoException('The object passed is not a file')
        response = self.copyto(query)
        for block in response.iter_content(DEFAULT_CHUNK_SIZE):
            file_object.write(block)

    def copyto_file_path(self, query, path, append=False):
        """
        Gets data from a table into a writable file object

        :param query: The "COPY { table_name [(column_name[, ...])] | ( query ) }
                           TO STDOUT [WITH(option[,...])]" query to execute
        :type query: str

        :param path: A path to a writable file
        :type path: str

        :param append: Whether to append or not if the file already exists
                       Default value is False
        :type append: bool

        :raise CartoException:
        """

        file_mode = 'wb' if not append else 'ab'
        with open(path, file_mode) as f:
            self.copyto_file_object(query, f)
