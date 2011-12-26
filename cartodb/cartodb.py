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

#REQUEST_TOKEN_URL = 'https://%(user)s.%(domain)s/oauth/request_token'
ACCESS_TOKEN_URL = '%(protocol)s://%(user)s.%(domain)s/oauth/access_token'
#AUTHORIZATION_URL = 'https://%(user)s.%(domain)s/oauth/authorize'
RESOURCE_URL = '%(protocol)s://%(user)s.%(domain)s/api/v1/sql'


class CartoDBException(Exception):
    pass

class CartoDB(object):
    """ basic client to access cartodb api """
    MAX_GET_QUERY_LEN = 2048

    def __init__(self, key, secret, email, password, cartodb_domain, host='carto.com', protocol='https'):

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
        access_token_url = ACCESS_TOKEN_URL % {'user': cartodb_domain, 'domain': host, 'protocol': protocol}
        resp, token = client.request(access_token_url, method="POST", body=urllib.urlencode(params))
        access_token = dict(urlparse.parse_qsl(token))
        token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])

        # prepare client
        self.resource_url = RESOURCE_URL % {'user': cartodb_domain, 'domain': host, 'protocol': protocol}
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



