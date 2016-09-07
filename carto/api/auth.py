import warnings
from pyrestcli.auth import BaseAuthClient


class APIKeyAuthClient(BaseAuthClient):
    """
    This class provides you with authenticated access to CARTO's APIs using your API key
    You can find your API key by clicking on the API key section of the user dropdown menu
    """
    def __init__(self, base_url, api_key, organization=None, proxies=None):
        """
        :param api_key: API key
        :return:
        """
        if not base_url.startswith("https"):
            warnings.warn("You are using unencrypted API key authentication!!!")

        self.organization = organization
        self.api_key = api_key

        super(APIKeyAuthClient, self).__init__(base_url, proxies=proxies)

    def send(self, relative_path, http_method, **requests_args):
        """
        Make a API-key-authorized request
        :param relative_path: URL path relative to self.base_url
        :param http_method: HTTP method
        :param requests_args: kargs to be sent to requests
        :return:
        """
        http_method = http_method.lower()
        if (http_method == "post" or http_method == "put") and "json" in requests_args:
            requests_args["json"].update({"api_key": self.api_key})
        else:
            if "params" not in requests_args:
                requests_args["params"] = {}
            requests_args["params"].update({"api_key": self.api_key})

        return super(APIKeyAuthClient, self).send(relative_path, http_method, **requests_args)
