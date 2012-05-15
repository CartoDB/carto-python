# -*- encoding: utf-8 -*-

"""
  ** CartoDBClient **

    A simple CartoDB client to perform requests against the CartoDB API.
    Internally it uses OAuth

  * Requirements:

     python 2.5
     pip install oauth2
     pip install simplejson # if you're running python < 2.6

  * Example use:
        user =  'your@mail.com'
        password =  'XXXX'
        CONSUMER_KEY='XXXXXXXXXXXXXXXXXX'
        CONSUMER_SECRET='YYYYYYYYYYYYYYYYYYYYYYYYYY'
        cartodb_domain = 'vitorino'
        cl = CartoDB(CONSUMER_KEY, CONSUMER_SECRET, user, password, cartodb_domain)
        print cl.sql('select * from a')

"""

import warnings
import urlparse
import oauth2 as oauth
import urllib
import httplib2
import urllib2
import sys

try:
    import json
except ImportError:
    import simplejson as json

from oauth2 import Request

#REQUEST_TOKEN_URL = 'https://%(user)s.%(domain)s/oauth/request_token'
ACCESS_TOKEN_URL = '%(protocol)s://%(user)s.%(domain)s/oauth/access_token'
#AUTHORIZATION_URL = 'https://%(user)s.%(domain)s/oauth/authorize'
RESOURCE_URL = '%(protocol)s://%(user)s.%(domain)s/api/v1/sql'


class CartoDBException(Exception):
    pass

class CartoDBBase(object):
    """ basic client to access cartodb api """
    MAX_GET_QUERY_LEN = 2048

    def __init__(self, cartodb_domain, host='cartodb.com', protocol='https'):
        self.resource_url = RESOURCE_URL % {'user': cartodb_domain, 'domain': host, 'protocol': protocol}

    def req(self, url, http_method="GET", http_headers=None, body=''):
        """
        this method should implement how to send a request to server using propper auth
        """
        raise NotImplementedError('req method must be implemented')

    def sql(self, sql, parse_json=True, do_post=True):
        """ executes sql in cartodb server
            set parse_json to False if you want raw reponse
        """
        p = urllib.urlencode({'q': sql})
        url = self.resource_url
        # depending on query size do a POST or GET
        if len(sql) < self.MAX_GET_QUERY_LEN and not do_post:
            url = url + '?' + p
            resp, content = self.req(url);
        else:
            resp, content = self.req(url, 'POST', body=p);

        if resp['status'] == '200':
            if parse_json:
                return json.loads(content)
            return content
        elif resp['status'] == '400':
            raise CartoDBException(json.loads(content)['error'])
        elif resp['status'] == '500':
            raise CartoDBException('internal server error')

        return None

class CartoDBOAuth(CartoDBBase):
    """
    This client allows to auth in cartodb using oauth. 
    """
    def __init__(self, key, secret, email, password, cartodb_domain, host='cartodb.com', protocol='https', proxy_info=None):
        super(CartoDBOAuth, self).__init__(cartodb_domain, host, protocol)

        self.consumer_key = key
        self.consumer_secret = secret
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)

        client = oauth.Client(consumer, proxy_info=proxy_info)
        client.set_signature_method = oauth.SignatureMethod_HMAC_SHA1()

        params = {}
        params["x_auth_username"] = email
        params["x_auth_password"] = password
        params["x_auth_mode"] = 'client_auth'

        # Get Access Token
        access_token_url = ACCESS_TOKEN_URL % {'user': cartodb_domain, 'domain': host, 'protocol': protocol}
        resp, token = client.request(access_token_url, method="POST", body=urllib.urlencode(params))
        access_token = dict(urlparse.parse_qsl(token))
        token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])

        # prepare client
        self.client = oauth.Client(consumer, token)


    def req(self, url, http_method="GET", http_headers=None, body=''):
        """ make an autorized request """
        resp, content = self.client.request(
            url,
            body=body,
            method=http_method,
            headers=http_headers
        )
        return resp, content

class CartoDBAPIKey(CartoDBBase):
    """
    this class provides you access to auth CartoDB API using your API. You can find your API key in https://USERNAME.cartodb.com/your_apps/api_key.
    this method is easier than use the oauth authentification but if less secure, it is recommended to use only using the https endpoint
    """

    def __init__(self, api_key, cartodb_domain, host='cartodb.com', protocol='https', proxy_info=None):
        super(CartoDBAPIKey, self).__init__(cartodb_domain, host, protocol)
        self.api_key = api_key
        self.client = httplib2.Http()
        if protocol != 'https':
            warnings.warn("you are using API key auth method with http") 


    def req(self, url, http_method="GET", http_headers={}, body=''):
        api_key_param = 'api_key=' + self.api_key
        if http_method == "POST":
            body = body + "&" + api_key_param
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            headers.update(http_headers)
            resp, content = self.client.request(url, "POST", body=body, headers=headers)
        else:
            url = url + "&" + api_key_param
            resp, content = self.client.request(url, headers=http_headers)

        return resp, content

