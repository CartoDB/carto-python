from .auth import NoAuthClient
from .core import CartoException


SQL_API_URL = '{api_version}/sql'
SQL_BATCH_API_URL = '{api_version}/sql/job/'


class SQLCLient(object):
    """
    Allows you to send requests to Carto's SQL API
    """
    def __init__(self, auth_client, api_version='v2'):
        """
        :param auth_client: Auth client to make authorized requests, such as APIKeyAuthClient
        :param sql_api_version: Current version is 'v2'. 'v1' can be used to avoid caching, but it's not guaranteed to work
        :return:
        """
        self.auth_client = auth_client
        self.api_url = SQL_API_URL.format(api_version=api_version)

    def send(self, sql, parse_json=True, do_post=True, format=None):
        """
        Executes SQL query in a Carto server
        :param sql:
        :param parse_json: Set it to False if you want raw reponse
        :param do_post: Set it to True to force post request
        :param format: Any of the data export formats allowed by Carto's SQL API
        :return: response data, either as json or as a regular response.content object
        """
        params = {'q': sql}
        if format:
            params['format'] = format
            if format not in ['json', 'geojson']:
                parse_json = False

        if len(sql) < self.auth_client.MAX_GET_QUERY_LEN and do_post is False:
            resp = self.auth_client.send(self.api_url, 'GET', params=params)
        else:
            resp = self.auth_client.send(self.api_url, 'POST', body=params)

        return self.auth_client.get_response_data(resp, parse_json)


class BatchSQLClient(object):
    def __init__(self, client, api_version='v2'):
        self.client = client
        if isinstance(self.client, NoAuthClient):
            raise CartoException("The client must be authenticated with an API key to access the batch sql api.")
        self.api_url = SQL_BATCH_API_URL.format(api_version=api_version)
        self.api_key = self.client.api_key

    def update_from_dict(self, data_dict):
        for k, v in data_dict.items():
            setattr(self, k, v)
        if "item_queue_id" in data_dict:
            self.id = data_dict["item_queue_id"]

    def send(self, url, http_method, json_body=None, http_header=None):
        data = self.client.send(url, http_method=http_method, http_headers=http_header, json=json_body)
        data_json = self.client.get_response_data(data)
        return data_json

    def create(self, sql_query):
        header = {'content-type': 'application/json'}
        data = self.send(self.api_url, http_method="POST", json_body={"query": sql_query}, http_header=header)
        return data

    def read(self, job_id):
        header = {'content-type': 'application/json'}
        data = self.send(self.api_url + job_id, http_method="GET", http_header=header)
        return data

    def update(self, job_id, sql_query):
        header = {'content-type': 'application/json'}
        data = self.send(self.api_url + job_id, http_method="PUT", json_body={"query": sql_query}, http_header=header)
        return data

    def cancel(self, job_id):
        confirmation = self.send(self.api_url + job_id, http_method="DELETE")
        return confirmation['status']


class BatchSQLManager(object):
    def __init__(self, client, api_version='v2'):
        self.client = client
        if isinstance(self.client, NoAuthClient):
            raise CartoException("The client must be authenticated with an API key to list the sql jobs.")
        self.api_key = self.client.api_key
        self.api_url = SQL_BATCH_API_URL.format(api_version=api_version)

    def all(self):
        data = self.client.send(self.api_url, "GET")
        data_json = self.client.get_response_data(data)
        return data_json
