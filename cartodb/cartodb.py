"""
  ** CartoDBClient **

    A simple CartoDB client to perform requests against the CartoDB API.
    Internally it uses OAuth

  * Requirements:

     python 2.6
     pip install -r requirements.txt

  * Example use:
        user =  'your@mail.com'
        password =  'XXXX'
        CONSUMER_KEY='XXXXXXXXXXXXXXXXXX'
        CONSUMER_SECRET='YYYYYYYYYYYYYYYYYYYYYYYYYY'
        cartodb_domain = 'vitorino'
        cl = CartoDBOAuth(CONSUMER_KEY, CONSUMER_SECRET, user, password, cartodb_domain)
        print cl.sql('select * from a')

"""
import httplib2
import warnings
import oauth2 as oauth
import requests
from requests_oauthlib import OAuth1Session

try:
    from urllib.parse import urlparse, parse_qsl, urlencode
except ImportError:
    # fall back to Python 2.x
    from urlparse import urlparse, parse_qsl
    from urllib import urlencode

try:
    import json
except ImportError:
    import simplejson as json

ACCESS_TOKEN_URL = '%(protocol)s://%(user)s.%(domain)s/oauth/access_token'
RESOURCE_URL = '%(protocol)s://%(user)s.%(domain)s/api/%(api_version)s/sql'
IMPORTS_URL = '%(protocol)s://%(user)s.%(domain)s/api/%(api_version)s/imports'


def proxyinfo2proxies(proxy_info):
    """
    Converts ProxyInfo object into a proxies dict
    :param proxy_info: ProxyInfo object
    :return: requests' proxies dict
    """
    proxies = {}

    if proxy_info.proxy_user and proxy_info.proxy_pass:
        credentials = "{user}:{password}@".format(user=proxy_info.proxy_user, password=proxy_info.proxy_pass)
    elif proxy_info.proxy_user:
        credentials = "{user}@".format(user=proxy_info.proxy_user)
    else:
        credentials = ''
    port = ":{port}".format(port=proxy_info.proxy_port) if proxy_info.proxy_port else ''

    proxy_url = "http://{credentials}{host}{port}".format(credentials=credentials, host=proxy_info.proxy_host, port=port)

    if proxy_info.applies_to("http"):
        proxies["http"] = proxy_url
    if proxy_info.applies_to("https"):
        proxies["https"] = proxy_url

    return proxies


def proxies2proxyinfo(proxies):
    """
    Converts proxies dict into a ProxyInfo object
    :param proxies: requests' proxies dict
    :return: ProxyInfo object
    """
    url_components = urlparse(proxies["http"]) if "http" in proxies else urlparse(proxies["https"])

    return httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_HTTP_NO_TUNNEL, url_components.hostname, url_components.port,
                              proxy_user=url_components.username, proxy_pass=url_components.password)


class CartoDBException(Exception):
    pass


class CartoDBBase(object):
    """ basic client to access cartodb api """
    MAX_GET_QUERY_LEN = 2048

    def __init__(self, cartodb_domain, host='cartodb.com', protocol='https', api_version=None, proxy_info=None, sql_api_version='v2', import_api_version='v1'):
        """
        :param cartodb_domain: Subdomain for API requests. It's called "cartodb_domain", but it's just a subdomain and doesn't have to live under cartodb.com
        :param host: Domain for API requests, even though it's called "host"
        :param protocol: Just use the default
        :param sql_api_version: Use default or 'v1' to avoid caching
        :param import_api_version: Only 'v1' is currently supported
        :param api_version: SQL API version, kept only for backward compatibility
        :param proxy_info: httplib2's ProxyInfo object or requests' proxy dict
        :return:
        """
        if api_version is None:
            api_version = sql_api_version
        self.resource_url = RESOURCE_URL % {'user': cartodb_domain, 'domain': host, 'protocol': protocol, 'api_version': api_version}
        self.imports_url = IMPORTS_URL % {'user': cartodb_domain, 'domain': host, 'protocol': protocol, 'api_version': import_api_version}
        self.host = host
        self.protocol = protocol
        self.api_version = api_version
        # For backwards compatibility, we need to support httplib2's ProxyInfo and requests' proxies objects
        # And we still need old-style ProxyInfo for the xAuth client
        if type(proxy_info) == httplib2.ProxyInfo:
            self.proxy_info = proxy_info
            self.proxies = proxyinfo2proxies(self.proxy_info)
        if type(proxy_info) == dict:
            self.proxies = proxy_info
            self.proxy_info = proxies2proxyinfo(self.proxies)
        else:
            self.proxy_info = None
            self.proxies = None

    def req(self, url, http_method="GET", http_headers=None, body=None, params=None, files=None):
        """
        Subclasses must implement this method, that will be used to send API requests with proper auth
        :param url: API URL, currently, only SQL API is supported
        :param http_method: "GET" or "POST"
        :param http_headers: requests' http_headers
        :param body: requests' "data"
        :param params: requests' "params"
        :param files: requests' "files"
        :return:
        """
        raise NotImplementedError('req method must be implemented')

    def get_response_data(self, resp, parse_json=True):
        """
        Get response data or throw an appropiate exception
        :param resp: requests' response object
        :param parse_json: if True, response will be parsed as JSON
        :return: response data, either as json or as a regular response.content object
        """
        if resp.status_code == requests.codes.ok:
            if parse_json:
                return resp.json()
            return resp.content
        elif resp.status_code == requests.codes.bad_request:
            r = resp.json()
            raise CartoDBException(r.get('error', False) or r.get('errors', 'Bad Request: ' + resp.text))
        elif resp.status_code == requests.codes.not_found:
            raise CartoDBException('Not found: ' + resp.url)
        elif resp.status_code == requests.codes.internal_server_error:
            raise CartoDBException('Internal server error')
        elif resp.status_code == requests.codes.unauthorized or resp.status_code == requests.codes.forbidden:
            raise CartoDBException('Access denied')
        else:
            raise CartoDBException('Unknown error occurred')

    def sql(self, sql, parse_json=True, do_post=True, format=None):
        """
        Executes SQL query in a CartoDB server
        :param sql:
        :param parse_json: Set it to False if you want raw reponse
        :param do_post: Set it to True to force post request
        :param format: Any of the data export formats allowed by CartoDB's SQL API
        :return: response data, either as json or as a regular response.content object
        """
        params = {'q': sql}
        if format:
            params['format'] = format
            if format not in ['json', 'geojson']:
                parse_json = False
        url = self.resource_url

        # depending on query size do a POST or GET
        if len(sql) < self.MAX_GET_QUERY_LEN and not do_post:
            resp = self.req(url, 'GET', params=params)
        else:
            resp = self.req(url, 'POST', body=params)

        return self.get_response_data(resp, parse_json)


class CartoDBOAuth(CartoDBBase):
    """
    This class provides you with authenticated access to CartoDB's APIs using your XAuth credentials.
    You can find your API key in https://USERNAME.cartodb.com/your_apps/oauth.
    """
    def __init__(self, key, secret, email, password, cartodb_domain, **kwargs):
        """
        :param key: XAuth consumer key
        :param secret: XAuth consumer secret
        :param email: User name on CartoDB (yes, no email)
        :param password: User password on CartoDB
        :param cartodb_domain: Subdomain for API requests. It's called "cartodb_domain", but it's just a subdomain and doesn't have to live under cartodb.com
        :param kwargs: Any other params to be sent to the parent class
        :return:
        """
        super(CartoDBOAuth, self).__init__(cartodb_domain, **kwargs)

        # Sadly, we xAuth is not supported by requests or any of its modules, so we need to stick to
        # oauth2 when it comes to getting the access token
        self.consumer_key = key
        self.consumer_secret = secret
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)

        client = oauth.Client(consumer, proxy_info=self.proxy_info)
        client.set_signature_method = oauth.SignatureMethod_HMAC_SHA1()

        params = {}
        params["x_auth_username"] = email
        params["x_auth_password"] = password
        params["x_auth_mode"] = 'client_auth'

        # Get Access Token
        access_token_url = ACCESS_TOKEN_URL % {'user': cartodb_domain, 'domain': self.host, 'protocol': self.protocol}
        resp, token = client.request(access_token_url, method="POST", body=urlencode(params))
        if resp['status'] != '200':
            raise CartoDBException("%s: %s" % (resp['status'], token))
        access_token = dict(parse_qsl(token.decode()))

        # Prepare client (now this is requests again!)
        try:
            self.client = OAuth1Session(self.consumer_key, client_secret=self.consumer_secret, resource_owner_key=access_token['oauth_token'],
                                        resource_owner_secret=access_token['oauth_token_secret'])
        except KeyError:
            raise CartoDBException('Access denied')

    def req(self, url, http_method="GET", http_headers=None, body=None, params=None, files=None):
        """
        Make a XAuth-authorized request
        :param url: API URL, currently, only SQL API is supported
        :param http_method: "GET" or "POST"
        :param http_headers: requests' http_headers
        :param body: requests' "data"
        :param params: requests' "params"
        :param files: requests' "files"
        :return: requests' response object
        """
        return self.client.request(http_method.lower(), url, params=params, data=body, headers=http_headers, proxies=self.proxies, files=files)


class CartoDBAPIKey(CartoDBBase):
    """
    This class provides you with authenticated access to CartoDB's APIs using your API key.
    You can find your API key in https://USERNAME.cartodb.com/your_apps/api_key.
    This method is easier than use the oauth authentification but if less secure, it is recommended to use only using the https endpoint
    """
    def __init__(self, api_key, cartodb_domain, **kwargs):
        """
        :param api_key: API key
        :param cartodb_domain: Subdomain for API requests. It's called "cartodb_domain", but it's just a subdomain and doesn't have to live under cartodb.com
        :param kwargs: Any other params to be sent to the parent class
        :return:
        """
        super(CartoDBAPIKey, self).__init__(cartodb_domain, **kwargs)

        self.api_key = api_key
        self.client = requests

        if self.protocol != 'https':
            warnings.warn("You are using unencrypted API key authentication!!!")

    def req(self, url, http_method="GET", http_headers=None, body=None, params=None, files=None):
        """
        Make a API-key-authorized request
        :param url: API URL, currently, only SQL API is supported
        :param http_method: "GET" or "POST"
        :param http_headers: requests' http_headers
        :param body: requests' "data"
        :param params: requests' "params"
        :param files: requests' "files"
        :return: requests' response object
        """
        params = params or {}
        params.update({"api_key": self.api_key})

        return self.client.request(http_method.lower(), url, params=params, data=body, headers=http_headers, proxies=self.proxies, files=files)
