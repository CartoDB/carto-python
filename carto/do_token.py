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
    bq_public_project = CharField()
    gcp_execution_project = CharField()
    bq_project = CharField()
    bq_dataset = CharField()
    gcs_bucket = CharField()
    instant_licensing = BooleanField()

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

    def get(self):
        return super(DoTokenManager, self).get('token')
