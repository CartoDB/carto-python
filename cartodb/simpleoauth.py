# -*- encoding: utf-8 -*-

"""
simple oauth client modified from oauth python library example
"""
import httplib
import time
import oauth.oauth as oauth
import urlparse, cgi
import urllib

class SimpleOAuthClient(oauth.OAuthClient):

    def __init__(self, server, port=httplib.HTTP_PORT, request_token_url='', access_token_url='', authorization_url=''):
        self.server = server
        self.port = port
        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorization_url = authorization_url
        self.connection = httplib.HTTPSConnection("%s:%d" % (self.server, self.port))

    def fetch_request_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        self.connection.request(oauth_request.http_method, self.request_token_url, headers=oauth_request.to_header()) 
        response = self.connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())

    def fetch_access_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        self.connection = httplib.HTTPSConnection("%s:%d" % (self.server, self.port))
        self.connection.request(oauth_request.http_method, self.access_token_url, headers=oauth_request.to_header()) 
        response = self.connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())

    def authorize_token(self, oauth_request):
        # via url
        # -> typically just some okay response
        self.connection.request(oauth_request.http_method, oauth_request.to_url()) 
        response = self.connection.getresponse()
        d = dict(response.getheaders())
        return d['location']
        #return response.read()

    def access_resource(self, oauth_request, url):
        # via post body
        # -> some protected resources
        self.connection = httplib.HTTPSConnection("%s:%d" % (self.server, self.port))
        headers = {'Content-Type' :'application/x-www-form-urlencoded'}
        self.connection.request('GET', url, body=oauth_request.to_postdata(), headers=headers)
        response = self.connection.getresponse()
        return response.read()
