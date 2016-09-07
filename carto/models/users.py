from gettext import gettext as _
from pyrestcli.resources import Resource, Manager
from pyrestcli.paginators import DummyPaginator  # Use CARTO's
from pyrestcli.fields import IntegerField, CharField, ResourceField

from carto.core import CartoException


API_VERSION = "v1"
API_ENDPOINT = "{api_version}/organization/{organization}/users/"


class UserField(ResourceField):
    value_class = "users.User"


class User(Resource):
    """
    Represents an enterprise CARTO user, i.e. a user that belongs to an organization
    Currently, CARTO's user API only supports enterprise users
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
        Sets the collection endpoint dynamically, based on provided organization (see api/auth.py)
        :param client: Auth client
        """
        if auth_client.organization is None:
            raise CartoException(_("User management requires an organization-enabled APIKeyAuthClient"))

        self.Meta.collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION, organization=auth_client.organization)
        super(User, self).__init__(auth_client)


class UserManager(Manager):
    """
    Manager for the User class
    """
    model_class = User
    paginator_class = DummyPaginator

    def filter(self, **search_args):
        """
        Should get all the current users from CARTO, but this is currently not supported by the API
        """
        raise CartoException(_("Retrieving user list is not currently supported by the API"))
