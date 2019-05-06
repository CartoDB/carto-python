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

from pyrestcli.fields import IntegerField, CharField, BooleanField

from .exceptions import CartoException
from .paginators import CartoPaginator
from .resources import Manager, WarnResource


API_VERSION = "v1"
API_ENDPOINT = "api/{api_version}/organization/{organization}/users/"
API_NONORG_ENDPOINT = "api/{api_version}/users/"


class User(WarnResource):
    """
    Represents an enterprise CARTO user, i.e. a user that belongs to an
    organization

    Currently, CARTO's user API only supports enterprise users.

    .. warning:: Non-public API. It may change with no previous notice
    """
    all_visualization_count = IntegerField()
    available_for_hire = BooleanField()
    avatar_url = CharField()
    base_url = CharField()
    db_size_in_bytes = IntegerField()
    description = CharField()
    disqus_shortname = CharField()
    email = CharField()
    google_maps_query_string = CharField()
    last_name = CharField()
    location = CharField()
    name = CharField()
    org_admin = BooleanField()
    org_user = BooleanField()
    password = CharField()
    public_visualization_count = IntegerField()
    quota_in_bytes = IntegerField()
    remove_logo = BooleanField()
    soft_geocoding_limit = IntegerField()
    table_count = IntegerField()
    twitter_username = CharField()
    username = CharField()
    viewer = BooleanField()
    website = CharField()

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
            self._api_endpoint = API_NONORG_ENDPOINT
        else:
            self._api_endpoint = API_ENDPOINT

        super(User, self).__init__(auth_client)

    def get_collection_endpoint(self):
        """
        """
        return self._api_endpoint.format(api_version=API_VERSION,
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

    def __init__(self, auth_client):
        """
        :param auth_client: Client to make (non)authorized requests
        :return:
        """
        super(UserManager, self).__init__(auth_client)
        if auth_client.organization is None:
            self._api_endpoint = API_NONORG_ENDPOINT
        else:
            self._api_endpoint = API_ENDPOINT

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
        return self._api_endpoint.format(api_version=API_VERSION,
                                   organization=self.client.organization)

    def get_resource_endpoint(self, resource_id):
        """
        """
        if resource_id is None:
            return None
        return urljoin(self.get_collection_endpoint(), str(resource_id))
