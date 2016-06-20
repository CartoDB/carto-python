import warnings
import requests

from .core import CartoException


class BaseAuthClient(object):
    """ Basic client to access Carto's APIs """
    MAX_GET_QUERY_LEN = 2048

    def __init__(self, user, host=None, domain='cartodb.com', protocol='https', import_api_version='v1', proxies=None):
        """
        :param user: Carto user name for API requests
        :param host: Host name for API requests
        :param protocol: Just use the default unless you really, really know what you're doing
        :param import_api_version: Only 'v1' is currently supported
        :param proxies: requests' proxy dict
        :return:
        """
        self.user = user
        self.domain = domain
        self.host = host
        self.protocol = protocol
        self.proxies = proxies
        self.client = requests

        if host is None and domain is not None:
            self.base_url = '{protocol}://{user}.{domain}/api/'.format(user=self.user, domain=self.domain, protocol=self.protocol)
        elif host is not None:
            self.base_url = '{protocol}://{host}/user/{user}/api/'.format(user=self.user, host=self.host, protocol=self.protocol)

    def send(self, url, http_method="GET", http_headers=None, body=None, params=None, files=None):
        """
        Subclasses must implement this method, that will be used to send API requests with proper auth
        :param url: API URL
        :param http_method: "GET" or "POST"
        :param http_headers: requests' http_headers
        :param body: requests' "data"
        :param params: requests' "params"
        :param files: requests' "files"
        :return:
        """
        raise NotImplementedError('send method must be implemented')

    def get_response_data(self, resp, parse_json=True):
        """
        Get response data or throw an appropiate exception
        :param resp: requests response object
        :param parse_json: if True, response will be parsed as JSON
        :return: response data, either as json or as a regular response.content object
        """
        if resp.status_code == requests.codes.ok:
            if parse_json:
                return resp.json()
            return resp.content
        elif resp.status_code == requests.codes.bad_request:
            r = resp.json()
            raise CartoException(r.get('error', False) or r.get('errors', 'Bad Request: ' + resp.text))
        elif resp.status_code == requests.codes.not_found:
            raise CartoException('Not found: ' + resp.url)
        elif resp.status_code == requests.codes.internal_server_error:
            raise CartoException('Internal server error')
        elif resp.status_code == requests.codes.unauthorized or resp.status_code == requests.codes.forbidden:
            raise CartoException('Access denied')
        else:
            raise CartoException('Unknown error occurred')


class NoAuthClient(BaseAuthClient):
    """
    This class provides you with unauthenticated access to Carto's APIs
    Please notice that currently only SQL API queries on public datasets will work without proper authentication
    """

    def send(self, relative_url, http_method="GET", http_headers=None, body=None, params=None):
        """
        Make a unauthorized request
        :param relative_url: API URL, relative to self.base_url
        :param http_method: "GET" or "POST"
        :param http_headers: requests' http_headers
        :param body: requests' "data"
        :param params: requests' "params"
        :return: requests' response object
        """
        url = self.base_url + relative_url

        return self.client.request(http_method.lower(), url, params=params, data=body, headers=http_headers, proxies=self.proxies)


class APIKeyAuthClient(BaseAuthClient):
    """
    This class provides you with authenticated access to Carto's APIs using your API key
    You can find your API key by clicking on the API key section of the user dropdown menu
    """
    def __init__(self, api_key, *args, **kwargs):
        """
        :param api_key: API key
        :return:
        """
        super(APIKeyAuthClient, self).__init__(*args, **kwargs)

        self.api_key = api_key

        if self.protocol != 'https':
            warnings.warn("You are using unencrypted API key authentication!!!")

    def send(self, relative_url, http_method="GET", http_headers=None, body=None, json=None, params=None, files=None):
        """
        Make a API-key-authorized request
        :param relative_url: API URL, relative to self.base_url
        :param http_method: "GET" or "POST"
        :param http_headers: requests' http_headers
        :param body: requests' "data"
        :param params: requests' "params"
        :param files: requests' "files"
        :return: requests' response object
        """
        url = self.base_url + relative_url

        params = params or {}
        params.update({"api_key": self.api_key})

        return self.client.request(http_method.lower(), url, params=params, data=body, json=json, headers=http_headers, proxies=self.proxies,
                                   files=files)
