SQL_API_URL = 'api/{api_version}/sql'
SQL_BATCH_API_URL = 'api/{api_version}/sql/job/'

MAX_GET_QUERY_LEN = 1024


class SQLClient(object):
    """
    Allows you to send requests to CARTO's SQL API
    """
    def __init__(self, auth_client, api_version='v2'):
        """
        :param auth_client: Auth client to make authorized requests, such as APIKeyAuthClient
        :param api_version: Current version is 'v2'. 'v1' can be used to avoid caching, but it's not guaranteed to work
        :return:
        """
        self.auth_client = auth_client
        self.api_url = SQL_API_URL.format(api_version=api_version)

        self.api_key = self.auth_client.api_key if hasattr(self.auth_client, "api_key") else None
        self.base_url = self.auth_client.base_url
        self.username = self.auth_client.username if hasattr(self.auth_client, "username") else None

    def send(self, sql, parse_json=True, do_post=True, format=None):
        """
        Executes SQL query in a CARTO server
        :param sql:
        :param parse_json: Set it to False if you want raw reponse
        :param do_post: Set it to True to force post request
        :param format: Any of the data export formats allowed by CARTO's SQL API
        :return: response data, either as json or as a regular response.content object
        """
        params = {'q': sql}
        if format:
            params['format'] = format
            if format not in ['json', 'geojson']:
                parse_json = False

        if len(sql) < MAX_GET_QUERY_LEN and do_post is False:
            resp = self.auth_client.send(self.api_url, 'GET', params=params)
        else:
            resp = self.auth_client.send(self.api_url, 'POST', data=params)

        return self.auth_client.get_response_data(resp, parse_json)


class BatchSQLClient(object):
    """
    Allows you to send requests to CARTO's Batch SQL API
    """
    def __init__(self, client, api_version='v2'):
        """
        :param client: Auth client to make authorized requests, such as APIKeyAuthClient
        :param api_version: Current version is 'v2'. 'v1' can be used to avoid caching, but it's not guaranteed to work
        :return:
        """
        self.client = client
        self.api_url = SQL_BATCH_API_URL.format(api_version=api_version)
        self.api_key = self.client.api_key if hasattr(self.client, "api_key") else None

    def update_from_dict(self, data_dict):
        """
        :param data_dict: Dictionary to be mapped into object attributes
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
        :param json_body: The information that needs to be sent, by default is set to None
        :param http_header: The header used to make write requests to the API, by default is none
        :return: Response data, either as json or as a regular response.content object
        """
        data = self.client.send(url, http_method=http_method, headers=http_header, json=json_body)
        data_json = self.client.get_response_data(data)
        return data_json

    def create(self, sql_query):
        """
        Creates a new batch SQL query
        :param sql_query: The query to be used
        :return: Response data, either as json or as a regular response.content object
        """
        header = {'content-type': 'application/json'}
        data = self.send(self.api_url, http_method="POST", json_body={"query": sql_query}, http_header=header)
        return data

    def read(self, job_id):
        """
        Reads the information for a specific Batch API request
        :param job_id: The id of the job to be read from
        :return: Response data, either as json or as a regular response.content object
        """
        data = self.send(self.api_url + job_id, http_method="GET")
        return data

    def update(self, job_id, sql_query):
        """
        Updates the sql query of a specific job
        :param job_id: The id of the job to be updated
        :param sql_query: The new sql query for the job
        :return: Response data, either as json or as a regular response.content object
        """
        header = {'content-type': 'application/json'}
        data = self.send(self.api_url + job_id, http_method="PUT", json_body={"query": sql_query}, http_header=header)
        return data

    def cancel(self, job_id):
        """
        Cancels a job
        :param job_id: The id of the job to be cancelled
        :return: A status code depending on whether the cancel request was successful
        """
        confirmation = self.send(self.api_url + job_id, http_method="DELETE")
        return confirmation['status']
