import re
import sys
import warnings
from pyrestcli.auth import BaseAuthClient
from .exceptions import CartoException

if sys.version_info >= (3,0):
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

class APIKeyAuthClient(BaseAuthClient):
    """
    This class provides you with authenticated access to CARTO's APIs using your API key
    You can find your API key by clicking on the API key section of the user dropdown menu
    """
    def __init__(self, base_url, api_key, organization=None, session=None):
        """
        :param base_url: Base URL. API endpoint paths will always be relative to this URL
        :param api_key: API key
        :param organization: For enterprise users, organization user belongs to
        :param session: requests' session object
        :return:
        """
        if not base_url.startswith("https"):
            warnings.warn("You are using unencrypted API key authentication!!!")

        self.organization = organization
        self.api_key = api_key

        # Make sure there is a trailing / for urljoin
        if not base_url.endswith('/'):
            base_url += '/'

        url_info = urlparse(base_url)
        # Cloud multiuser organization:
        #   /u/<username>
        # On-Prem:
        #   /user/<username>
        m = re.search('^/u(?:ser)?/([^/]+)/.*$', url_info.path)
        if m is None:
            # Cloud personal account
            # <username>.carto.com
            netloc = url_info.netloc
            if netloc.startswith('www.'):
                netloc = netloc.split('www.')[1]
            m = re.search('^(.*?)\..*', netloc)
        self.username = m.group(1)

        super(APIKeyAuthClient, self).__init__(base_url, session=session)

    def send(self, relative_path, http_method, **requests_args):
        """
        Make a API-key-authorized request
        :param relative_path: URL path relative to self.base_url
        :param http_method: HTTP method
        :param requests_args: kwargs to be sent to requests
        :return:
        :raise CartoException:
        """
        try:
            http_method = http_method.lower()
            if (http_method == "post" or http_method == "put") and "json" in requests_args:
                requests_args["json"].update({"api_key": self.api_key})
            else:
                if "params" not in requests_args:
                    requests_args["params"] = {}
                requests_args["params"].update({"api_key": self.api_key})

            return super(APIKeyAuthClient, self).send(relative_path, http_method, **requests_args)
        except Exception as e:
            raise CartoException(e)
