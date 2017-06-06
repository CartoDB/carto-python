"""
Module for working with users

.. module:: carto.users
   :platform: Unix, Windows
   :synopsis: Module for working with users

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from gettext import gettext as _
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from pyrestcli.fields import IntegerField, CharField

from .exceptions import CartoException
from .paginators import CartoPaginator
from .resources import Manager, WarnResource


API_VERSION = "v1"
API_ENDPOINT = "api/{api_version}/organization/{organization}/users/"


class User(WarnResource):
    """
    Represents an enterprise CARTO user, i.e. a user that belongs to an
    organization

    Currently, CARTO's user API only supports enterprise users.

    .. warning:: Non-public API. It may change with no previous notice
    """
    username = CharField()
    email = CharField()
    avatar_url = CharField()
    base_url = CharField()
    quota_in_bytes = IntegerField()
    db_size_in_bytes = IntegerField()
    table_count = IntegerField()
    public_visualization_count = IntegerField()
    all_visualization_count = IntegerField()
    password = CharField()
    soft_geocoding_limit = IntegerField()

    class Meta:
        id_field = "username"
        name_field = "username"

    def __init__(self, auth_client):
        """
        Sets the collection endpoint dynamically, based on provided
        organization (see api/auth.py)
        :param auth_client: Auth client
        """
        if auth_client.organization is None:
            raise CartoException(_("User management requires an \
                                   organization-enabled APIKeyAuthClient"))

        super(User, self).__init__(auth_client)

    def get_collection_endpoint(self):
        """
        """
        return API_ENDPOINT.format(api_version=API_VERSION,
                                   organization=self.client.organization)

    def get_resource_endpoint(self):
        """
        """
        resource_id = getattr(self, self.Meta.id_field, None)
        if resource_id is None:
            return None
        return urljoin(self.get_collection_endpoint(), str(resource_id))


class UserManager(Manager):
    """
    Manager for the User class.

    .. warning:: Non-public API. It may change with no previous notice
    """
    resource_class = User
    paginator_class = CartoPaginator

    def filter(self, **search_args):
        """
        Should get all the current users from CARTO, but this is currently not
        supported by the API
        """
        raise CartoException(_("Retrieving user list is not currently \
                               supported by the API"))

    def get_collection_endpoint(self):
        """
        """
        return API_ENDPOINT.format(api_version=API_VERSION,
                                   organization=self.client.organization)

    def get_resource_endpoint(self, resource_id):
        """
        """
        if resource_id is None:
            return None
        return urljoin(self.get_collection_endpoint(), str(resource_id))
