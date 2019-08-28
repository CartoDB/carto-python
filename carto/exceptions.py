"""
Module for carto-python exceptions definitions

.. module:: carto.exceptions
   :platform: Unix, Windows
   :synopsis: Module for carto-python exceptions definitions

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""
from requests import codes

class CartoException(Exception):
    """
    Any Exception produced by carto-python should be wrapped around this class
    """
    pass


class CartoRateLimitException(CartoException):
    """
    This exception is raised when a request is rate limited by SQL or Maps APIs (429 Too Many Requests HTTP error).
    More info about CARTO rate limits: https://carto.com/developers/fundamentals/limits/#rate-limits

    It extends CartoException with the rate limits info, so that any client can manage
    when to retry a rate limited request.
    """
    def __init__(self, response):
        """
        Init method

        :param response: The response rate limited by CARTO APIs
        :type response: requests.models.Response class

        :return:
        """
        super(CartoRateLimitException, self).__init__(response.text)
        self.limit = int(response.headers['Carto-Rate-Limit-Limit'])
        self.remaining = int(response.headers['Carto-Rate-Limit-Remaining'])
        self.retry_after = int(response.headers['Retry-After'])
        self.reset = int(response.headers['Carto-Rate-Limit-Reset'])

    @staticmethod
    def is_rate_limited(response):
        """
        Checks if the response has been rate limited by CARTO APIs

        :param response: The response rate limited by CARTO APIs
        :type response: requests.models.Response class

        :return: Boolean
        """
        if (response.status_code == codes.too_many_requests and 'Retry-After' in response.headers and
                int(response.headers['Retry-After']) >= 0):
            return True

        return False
