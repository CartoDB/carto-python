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

import urlparse
import oauth2 as oauth
import urllib
import httplib2
import sys

try:
    import json
except ImportError:
    import simplejson as json

from oauth2 import Request

REQUEST_TOKEN_URL = 'https://%(user)s.cartodb.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://%(user)s.cartodb.com/oauth/access_token'
AUTHORIZATION_URL = 'https://%(user)s.cartodb.com/oauth/authorize'
RESOURCE_URL = 'https://%(user)s.cartodb.com/api/v1/sql'


class CartoDB(object):
    """ basic client to access cartodb api """

    def __init__(self, key, secret, email, password, cartodb_domain):

        self.consumer_key = key
        self.consumer_secret = secret
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)

        client = oauth.Client(consumer)
        client.set_signature_method = oauth.SignatureMethod_HMAC_SHA1()

        params = {}
        params["x_auth_username"] = email
        params["x_auth_password"] = password
        params["x_auth_mode"] = 'client_auth'

        # Get Access Token
        access_token_url = ACCESS_TOKEN_URL % {'user': cartodb_domain}
        resp, token = client.request(access_token_url, method="POST", body=urllib.urlencode(params))
        access_token = dict(urlparse.parse_qsl(token))
        token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])

        # prepare client
        self.resource_url = RESOURCE_URL % {'user': cartodb_domain}
        self.client = oauth.Client(consumer, token)


    def req(self, url, http_method="GET", http_headers=None):
        """ make an autorized request """
        resp, content = self.client.request(
            url,
            method=http_method,
            headers=http_headers
        )
        return resp, content

    def sql(self, sql, parse_json=True):
        """ executes sql in cartodb server
            set parse_json to False if you want raw reponse
        """
        p = urllib.urlencode({'q': sql})
        url = self.resource_url + '?' + p
        resp, content = self.req(url);
        if resp['status'] == '200':
            if parse_json:
                return json.loads(content)
            return content
        return None



