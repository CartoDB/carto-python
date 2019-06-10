"""
Module for working with custom map visualizations (aka Kuvizs)

.. module:: carto.Kuvizs
   :platform: Unix, Windows
   :synopsis: Module for working with custom map visualizations (aka Kuvizs)

.. moduleauthor:: Simon Martin <simon@carto.com>

"""

from pyrestcli.fields import CharField, DateTimeField

from .fields import Base64EncodedField
from .resources import Manager, WarnResource
from .paginators import CartoPaginator


API_VERSION = "v4"
API_ENDPOINT = "api/{api_version}/kuviz/"

PRIVACY_PUBLIC = 'public'
PRIVACY_PASSWORD = 'password'


class Kuviz(WarnResource):
    """
    Represents a custom map visualization in CARTO.

    .. warning:: Non-public API. It may change with no previous notice
    """
    created_at = DateTimeField()
    data = Base64EncodedField()
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

    .. warning:: Non-public API. It may change with no previous notice
    """
    resource_class = Kuviz
    paginator_class = CartoPaginator
    json_collection_attribute = 'visualizations'

    def get(self, id):
        """
        Not implemented
        """
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
        if password:
            return super(KuvizManager, self).create(data=html, name=name,
                                                    privacy=PRIVACY_PASSWORD, password=password)
        else:
            return super(KuvizManager, self).create(data=html, name=name)
