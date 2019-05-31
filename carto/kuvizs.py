"""
Module for working with map custom visualizations (aka Kuvizs)

.. module:: carto.Kuvizs
   :platform: Unix, Windows
   :synopsis: Module for working with map custom visualizations (aka Kuvizs)

.. moduleauthor:: Simon Martin <simon@carto.com>

"""

import base64

from pyrestcli.fields import CharField, DateTimeField

from .resources import Manager, WarnResource
from .paginators import CartoPaginator


API_VERSION = "v4"
API_ENDPOINT = "api/{api_version}/kuviz/"

PRIVACY_PASSWORD = 'password'

class Kuviz(WarnResource):
    """
    Represents a map custom visualization in CARTO.
    """
    created_at = DateTimeField()
    data = CharField()
    id = CharField()
    name = CharField()
    password = CharField()
    privacy = CharField()
    updated_at = DateTimeField()
    url = CharField()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "id"


class KuvizManager(Manager):
    """
    Manager for the Kuviz class.
    """
    resource_class = Kuviz
    paginator_class = CartoPaginator

    def get(self):
        pass

    def filter(self, **search_args):
        pass

    def all(self):
        pass

    def create(self, html, name, password=None):
        """
        Creates a Kuviz.

        :param html: The visualization HTML
        :param name: The visualization name
        :type html: str
        :type name: str

        :return: A Kuviz instance with the `url` and `visualization` properties
                    of the new Kuviz
        """
        data = base64.b64encode(html.encode()).decode('ascii')
        if password:
            return super(KuvizManager, self).create(data=data, name=name,
                                                    privacy=PRIVACY_PASSWORD, password=password)
        else:
            return super(KuvizManager, self).create(data=data, name=name)