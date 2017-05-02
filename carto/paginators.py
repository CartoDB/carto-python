"""
Used internally to retrieve results paginated

.. module:: carto.paginators
   :platform: Unix, Windows
   :synopsis: Used internally to retrieve results paginated

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from pyrestcli.paginators import Paginator


class CartoPaginator(Paginator):
    """
    Used internally to retrieve results paginated

    """
    def __init__(self, json_collection_attribute, base_url, params=None):
        self.json_collection_attribute = json_collection_attribute

        super(CartoPaginator, self).__init__(base_url, params)

    def get_urls(self, initial_url):
        self.url = initial_url
        self.total_count = 0
        self.page = 1

        while self.url is not None:
            yield self.url, {"page": self.page}

    def process_response(self, response):
        response_json = response.json()
        self.total_count += len(response_json[self.json_collection_attribute])

        try:
            total_count_from_api = int(response_json["total_user_entries"])
        except KeyError:
            total_count_from_api = int(response_json["total_entries"])

        if self.total_count < total_count_from_api:
            self.page += 1
        else:
            self.url = None

        return response
