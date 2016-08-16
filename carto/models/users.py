from gettext import gettext as _

from carto.core import Resource, Manager, CartoException


API_VERSION = "v1"
API_ENDPOINT = "{api_version}/organization/{organization}/users/"


class User(Resource):
    """
    Represents an enterprise CARTO user, i.e. a user that belongs to an organization
    Currently, CARTO's user API only supports enterprise users
    """
    fields = ("id", "username", "email", "avatar_url", "base_url", "quota_in_bytes", "db_size_in_bytes", "table_count", "public_visualization_count",
              "all_visualization_count", "password", "soft_geocoding_limit")

    def __str__(self):
        """
        Let's use the username for a more meaningful representation
        :return: Properly-encoded username
        """
        try:
            return unicode(self.username).encode("utf-8")
        except AttributeError:
            return super(User, self).__str__()

    def __init__(self, client):
        """
        Sets the collection endpoint dynamically, based on provided organization (see api/auth.py)
        :param client: Auth client
        """
        if client.organization is None:
            raise CartoException(_("User management requires an organization-enabled APIKeyAuthClient"))

        self.collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION, organization=client.organization)
        super(User, self).__init__(client)

    @property
    def resource_endpoint(self):
        """
        Users have ids, but endpoints are built using the user name
        :return: Relative endpoint for the user
        """
        return self.get_resource_endpoint(self.username) if self.username is not None and self._id is not None else None


class UserManager(Manager):
    """
    Manager for the User class
    """
    model_class = User

    def __init__(self, client):
        """
        Sets the collection endpoint dynamically, based on provided organization (see api/auth.py)
        :param client: Auth client
        """
        if client.organization is None:
            raise CartoException(_("User management requires an organization-enabled APIKeyAuthClient"))

        self.collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION, organization=client.organization)
        super(UserManager, self).__init__(client)

    def all(self):
        """
        Should get all the current users from CARTO, but this is currently not supported by the API
        """
        raise CartoException(_("Retrieving user list is not currently supported by the API"))
