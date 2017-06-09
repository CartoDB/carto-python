"""
Module for authenticated access to CARTO's APIs

.. module:: carto.auth
   :platform: Unix, Windows
   :synopsis: Module for authenticated access to CARTO's APIs

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from gettext import gettext as _
import re
import sys
import warnings

from pyrestcli.auth import BaseAuthClient

from .exceptions import CartoException

if sys.version_info >= (3, 0):
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


class APIKeyAuthClient(BaseAuthClient):
    """
    This class provides you with authenticated access to CARTO's APIs using
    your API key.

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
        if not base_url.startswith("https"):
            warnings.warn("You are using unencrypted API key \
                          authentication!!!")

        self.organization = organization
        self.api_key = api_key

        # Make sure there is a trailing / for urljoin
        if not base_url.endswith('/'):
            base_url += '/'

        self.username = self.get_user_name(base_url)

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
            http_method = http_method.lower()
            if (http_method in ['post', 'put']) and "json" in requests_args:
                requests_args["json"].update({"api_key": self.api_key})
            else:
                if "params" not in requests_args:
                    requests_args["params"] = {}
                requests_args["params"].update({"api_key": self.api_key})

            return super(APIKeyAuthClient, self).send(relative_path,
                                                      http_method,
                                                      **requests_args)
        except Exception as e:
            raise CartoException(e)

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
