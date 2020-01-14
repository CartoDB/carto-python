"""
Module for working with custom map visualizations (aka Kuvizs)

.. module:: carto.Kuvizs
   :platform: Unix, Windows
   :synopsis: Module for working with custom map visualizations (aka Kuvizs)

.. moduleauthor:: Simon Martin <simon@carto.com>

"""

from pyrestcli.fields import CharField, DateTimeField

from .fields import Base64EncodedField, PasswordAndPrivacyFields
from .resources import Manager, WarnResource
from .paginators import CartoPaginator


API_VERSION = "v4"
API_ENDPOINT = "api/{api_version}/kuviz/"

IF_EXISTS_FAIL = "fail"
IF_EXISTS_REPLACE = "replace"


class Kuviz(WarnResource):
    """
    Represents a custom map visualization in CARTO.

    .. warning:: Non-public API. It may change with no previous notice
    """
    created_at = DateTimeField()
    data = Base64EncodedField()
    id = CharField()
    name = CharField()
    password = PasswordAndPrivacyFields()
    privacy = CharField()
    updated_at = DateTimeField()
    url = CharField()
    if_exists = CharField()

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

    def create(self, html, name, password=None, if_exists=IF_EXISTS_FAIL):
        """
        Creates a Kuviz.

        :param html: The visualization HTML
        :param name: The visualization name
        :param password: The visualization password
        :param if_exists: Behavior in case a publication with the same name already exists in your account.
            The options are: 'fail' or 'replace'. Default is 'fail'.
        :type html: str
        :type name: str
        :type password: str
        :type if_exists: str

        :return: A Kuviz instance with the `url` and `visualization` properties
                    of the new Kuviz
        """
        return super(KuvizManager, self).create(data=html, name=name, password=password, if_exists=if_exists)
