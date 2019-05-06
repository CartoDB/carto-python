# -*- coding: utf-8 -*-
"""
Module for authenticated access to CARTO's APIs

.. module:: carto.auth
   :platform: Unix, Windows
   :synopsis: Module for authenticated access to CARTO's APIs

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>
.. moduleauthor:: Juan Ignacio Sánchez <juanignaciosl@carto.com>


"""

from gettext import gettext as _
import re
import sys
import warnings
import pkg_resources

from pyrestcli.auth import BaseAuthClient, BasicAuthClient
from .exceptions import CartoException, CartoRateLimitException

if sys.version_info >= (3, 0):
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


class _UsernameGetter:
    def get_user_name(self, base_url):
        try:
            url_info = urlparse(base_url)
            # On-Prem:
            #   /user/<username>
            m = re.search('^/user/([^/]+)/.*$', url_info.path)
            if m is None:
                # Cloud personal account (org and standalone)
                # <username>.carto.com
                netloc = url_info.netloc
                if netloc.startswith('www.'):
                    netloc = netloc.split('www.')[1]
                m = re.search('^(.*?)\..*', netloc)
            return m.group(1)
        except Exception:
            raise CartoException(_("Could not find a valid user_name in the " +
                                   "base URL provided. Please check that the" +
                                   "URL is one of " +
                                   "'https://{user_name}.carto.com', " +
                                   "'https://carto.com/user/{user_name}' " +
                                   "or a similar one based on your domain"))


class _BaseUrlChecker:
    def check_base_url(self, base_url):
        if not base_url.startswith("https"):
            warnings.warn("You are using unencrypted API key \
                          authentication!!!")
        # Make sure there is a trailing / for urljoin
        if not base_url.endswith('/'):
            base_url += '/'

        return base_url


class _ClientIdentifier:

    CARTO_VERSION = pkg_resources.require('carto')[0].version

    def get_user_agent(self, name='carto-python-sdk'):
        return "{name}/{version}".format(
            name=name,
            version=self.CARTO_VERSION)

    def get_client_identifier(self, prefix='cps'):
        return "{prefix}-{version}".format(
            prefix=prefix,
            version=self.CARTO_VERSION)


class APIKeyAuthClient(_UsernameGetter, _BaseUrlChecker, _ClientIdentifier,
                       BaseAuthClient):
    """
    This class provides you with authenticated access to CARTO's APIs using
    your API key.

    You can find your API key by clicking on the API key section of the user
    dropdown menu
    """
    def __init__(self, base_url, api_key, organization=None, session=None,
                 client_id=None, user_agent=None):
        """
        Init method

        :param base_url: Base URL. API endpoint paths will always be relative
        to this URL
        :param api_key: API key
        :param organization: For enterprise users, organization user belongs to
        :param session: requests' session object
        :param client_id: Client param string to pass for request args
        :param user_agent: User-Agent param string to pass for request args
        :type api_key: str
        :type organization: str
        :type session: object
        :type client_id: str
        :type user_agent: str

        :return:
        """
        self.organization = organization
        self.api_key = api_key
        base_url = self.check_base_url(base_url)
        self.username = self.get_user_name(base_url)

        if user_agent is None:
            self.user_agent = self.get_user_agent()
        else:
            self.user_agent = user_agent

        if client_id is None:
            self.client_id = self.get_client_identifier()
        else:
            self.client_id = client_id

        super(APIKeyAuthClient, self).__init__(base_url, session=session)

    def send(self, relative_path, http_method, **requests_args):
        """
        Makes an API-key-authorized request

        :param relative_path: URL path relative to self.base_url
        :param http_method: HTTP method
        :param requests_args: kwargs to be sent to requests
        :type relative_path: str
        :type http_method: str
        :type requests_args: kwargs

        :return:
            A request response object
        :raise:
            CartoException
        """
        try:
            http_method, requests_args = self.prepare_send(http_method, **requests_args)

            response = super(APIKeyAuthClient, self).send(relative_path, http_method, **requests_args)
        except Exception as e:
            raise CartoException(e)

        if CartoRateLimitException.is_rate_limited(response):
            raise CartoRateLimitException(response)

        return response

    def prepare_send(self, http_method, **requests_args):
        http_method = http_method.lower()
        params = {
            "api_key": self.api_key,
            "client": self.client_id
        }
        if (http_method in ['post', 'put']) and "json" in requests_args:
            requests_args["json"].update(params)
        else:
            if "params" not in requests_args:
                requests_args["params"] = {}
            requests_args["params"].update(params)

        if not requests_args.get('headers', None):
            requests_args['headers'] = {}
        requests_args['headers'].update({'User-Agent': self.user_agent})

        return http_method, requests_args


class NonVerifiedAPIKeyAuthClient(APIKeyAuthClient):
    """
    This class provides you with authenticated access to CARTO's APIs using
    your API key but avoids verifying SSL certificates. This is useful for onpremises instances of CARTO

    You can find your API key by clicking on the API key section of the user
    dropdown menu
    """
    def __init__(self, base_url, api_key, organization=None, session=None):
        """
        Init method

        :param base_url: Base URL. API endpoint paths will always be relative
        to this URL
        :param api_key: API key
        :param organization: For enterprise users, organization user belongs to
        :param session: requests' session object
        :type api_key: str
        :type organization: str

        :return:
        """
        super(NonVerifiedAPIKeyAuthClient, self).__init__(base_url, api_key, organization, session)

    def send(self, relative_path, http_method, **requests_args):
        """
        Makes an API-key-authorized request not verifying SSL certs

        :param relative_path: URL path relative to self.base_url
        :param http_method: HTTP method
        :param requests_args: kwargs to be sent to requests
        :type relative_path: str
        :type http_method: str
        :type requests_args: kwargs

        :return:
            A request response object
        :raise:
            CartoException
        """
        try:
            http_method, requests_args = self.prepare_send(http_method, **requests_args)
            requests_args["verify"] = False
            response = super(APIKeyAuthClient, self).send(relative_path, http_method, **requests_args)
        except Exception as e:
            raise CartoException(e)

        if CartoRateLimitException.is_rate_limited(response):
            raise CartoRateLimitException(response)

        return response


class AuthAPIClient(_UsernameGetter, _BaseUrlChecker, BasicAuthClient):
    """
    This class provides you with authenticated access to CARTO's APIs using
    your API key at Basic authentication header, as provided by Auth API.

    Auth API is still under development. You might want to take a look at
    APIKeyAuthClient for missing features or an stable API.

    You can find your API key by clicking on the API key section of the user
    dropdown menu
    """

    def __init__(self, base_url, api_key, organization=None, session=None):
        """
        Init method

        :param base_url: Base URL. API endpoint paths will always be relative
        to this URL
        :param api_key: API key
        :param organization: For enterprise users, organization user belongs to
        :param session: requests' session object
        :type api_key: str
        :type organization: str

        :return:
        """
        self.organization = organization
        self.api_key = api_key
        base_url = self.check_base_url(base_url)
        self.username = self.get_user_name(base_url)

        super(AuthAPIClient, self).__init__(self.username, api_key, base_url, session=session)

    def is_valid_api_key(self):
        """
        Checks validity. Right now, an API key is considered valid if it
        can list user API keys and the result contains that API key.
        This might change in the future.

        :return: True if the API key is considered valid for current user.
        """
        res = self.send('api/v3/api_keys', 'get')
        return \
            res.ok and \
            self.api_key in (ak['token'] for ak in res.json()['result'])
