"""
Module for carto-python exceptions definitions

.. module:: carto.exceptions
   :platform: Unix, Windows
   :synopsis: Module for carto-python exceptions definitions

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""


class CartoException(Exception):
    """
    Any Exception produced by carto-python should be wrapped around this class
    """
    pass


class CartoRateLimitException(CartoException):
    def __init__(self, exception, response):
        super()
        self.limit = response.headers['Carto-Rate-Limit-Limit']
        self.remaining = response.headers['Carto-Rate-Limit-Remaining']
        self.retryAfter = response.headers['Retry-After']
        self.reset = response.headers['Carto-Rate-Limit-Reset']

    @staticmethod
    def isResponseRateLimited(response):
        if (response.status_code == 429 and
            'Retry-After' in response.headers and
            int(response.headers['Retry-After']) >= 0):
            return True

        return False
