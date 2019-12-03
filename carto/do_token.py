"""
Module for working with Data Observatory tokens

.. module:: carto.DoToken
   :platform: Unix, Windows
   :synopsis: Module for working with Data Observatory tokens

.. moduleauthor:: Simon Martin <simon@carto.com>

"""

from pyrestcli.fields import CharField, BooleanField

from .paginators import CartoPaginator
from .resources import WarnResource, Manager


API_VERSION = "v4"
API_ENDPOINT = "api/{api_version}/do/token"


class DoToken(WarnResource):
    """
    Represents a Data Observatory token in CARTO.

    .. warning:: Non-public API. It may change with no previous notice
    """
    access_token = CharField()
    public_data_project = CharField()
    execution_project = CharField()
    user_data_project = CharField()
    dataset = CharField()
    bucket = CharField()
    speed_licensing = BooleanField()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "access_token"


class DoTokenManager(Manager):
    """
    Manager for the DoToken class.

    .. warning:: Non-public API. It may change with no previous notice
    """
    resource_class = DoToken
    json_collection_attribute = None
    paginator_class = CartoPaginator
