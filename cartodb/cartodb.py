# -*- encoding: utf-8 -*-

"""
  ** CartoDBClient **
 
    A simple CartoDB client to perform requests against the CartoDB API.
    Internally it uses OAuth

  * Requirements:

     python 2.5 
     pip install oauth

  * Example use:
     from cartodb import CartoDB
     db = CartoDB(CONSUMER_KEY, CONSUMER_SECRET)
     print db.run_sql("select * from test")

"""

import httplib
import time
import oauth.oauth as oauth
import urlparse, cgi
import urllib

from simpleoauth import SimpleOAuthClient

SERVER = 'api.cartodb.com'
PORT = 443

REQUEST_TOKEN_URL = 'https://api.cartodb.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.cartodb.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.cartodb.com/oauth/authorize'
CALLBACK_URL = 'http://foobar.com'
RESOURCE_URL = 'https://api.cartodb.com/v1' 


class CartoDB(object):
    """ base client to access cartodb api """

    def __init__(self, key, secret):
        self.token = self.get_access_token(key, secret)

    def get_access_token(self, key, secret):
        self.client = client = SimpleOAuthClient(SERVER, PORT, REQUEST_TOKEN_URL, ACCESS_TOKEN_URL, AUTHORIZATION_URL)
        consumer = self.consumer = oauth.OAuthConsumer(key, secret)
        signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
        self.signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, callback=CALLBACK_URL, http_url=client.request_token_url)
        oauth_request.sign_request(self.signature_method_hmac_sha1, consumer, None)
        token = client.fetch_request_token(oauth_request)
        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url=client.authorization_url)
        # this will actually occur only on some callback
        response = client.authorize_token(oauth_request)
        # sad way to get the verifier
        query = urlparse.urlparse(response)[4]
        params = cgi.parse_qs(query, keep_blank_values=False)
        verifier = params['oauth_verifier'][0]

        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, verifier=verifier, http_url=client.access_token_url)
        oauth_request.sign_request(self.signature_method_hmac_sha1, consumer, token)
        token = client.fetch_access_token(oauth_request)
        return token

    def get_resource(self, resource, parameters=None):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.token, http_method='GET', http_url=resource, parameters=parameters)
        oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, self.token)
        params = self.client.access_resource(oauth_request, resource)
        return params

    def run_sql(self, sql):
        """ executes sql query on cartodb server and return json """
        p = urllib.urlencode({'sql': sql})
        #TODO: parse json and return python objects
        return self.get_resource(RESOURCE_URL + '?' + p)

if __name__ == '__main__':
    db = CartoDB(CONSUMER_KEY, CONSUMER_SECRET)
    print db.run_sql("select * from test")
