"""
Module for working with CARTO OAuth app management API

https://carto.com/developers/oauth/apps/

.. module:: carto.oauth_apps
   :platform: Unix, Windows
   :synopsis: Module for working with CARTO OAuth app management API

.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from pyrestcli.fields import CharField, DateTimeField, BooleanField

from .resources import Resource, Manager
from .exceptions import CartoException
from .paginators import CartoPaginator


API_VERSION = "v4"
API_ENDPOINT = "api/{api_version}/oauth_apps/"
GRANTED_API_ENDPOINT = "api/{api_version}/granted_oauth_apps/"


class OauthApp(Resource):
    """
    Represents an OAuth app in CARTO.

    """
    id = CharField()
    name = CharField()
    client_id = CharField()
    client_secret = CharField()
    user_id = CharField()
    user_name = CharField()
    redirect_uris = CharField(many=True)
    icon_url = CharField()
    restricted = BooleanField()
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "id"

    def regenerate_client_secret(self):
        """
        Regenerates the associated client secret

        :return:

        :raise: CartoException
        """
        try:
            endpoint = (self.Meta.collection_endpoint
                        + "{id}/regenerate_secret"). \
                format(id=self.id)

            self.send(endpoint, "POST")
        except Exception as e:
            raise CartoException(e)


class GrantedOauthApp(Resource):
    """
    Represents an OAuth app granted to access a CARTO account.

    """
    id = CharField()
    name = CharField()
    icon_url = CharField()
    scopes = CharField(many=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        collection_endpoint = GRANTED_API_ENDPOINT.format(api_version=API_VERSION)
        app_collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "id"

    def revoke(self):
        """
        Revokes the access of the OAuth app to the CARTO account of the user

        :return:

        :raise: CartoException
        """
        try:
            endpoint = (self.Meta.app_collection_endpoint
                        + "{id}/revoke"). \
                format(id=self.id)

            self.send(endpoint, "POST")
        except Exception as e:
            raise CartoException(e)

    def save(self):
        pass

    def refresh(self):
        pass

    def delete(self):
        pass


class OauthAppManager(Manager):
    """
    Manager for the OauthApp class.

    """
    resource_class = OauthApp
    json_collection_attribute = "result"
    paginator_class = CartoPaginator

    def create(self, name, redirect_uris, icon_url):
        """
        Creates an OauthApp.

        :param name: The OAuth app name
        :param redirect_uris: An array of URIs for authorize callback.
        :param icon_url: A URL with a squared icon for the Oauth app.
        :type name: str
        :type redirect_uris: list
        :type icon_url: str

        :return: An OauthApp instance with a client_id and client_secret
        """
        return super(OauthAppManager, self).create(name=name, redirect_uris=redirect_uris, icon_url=icon_url)

    def all_granted(self):
        """
        Lists granted OAuth apps to access the user CARTO account.

        :return: A list of GrantedOauthApp
        """
        raw_resources = []

        for url, paginator_params in self.paginator.get_urls(GrantedOauthApp.Meta.collection_endpoint):
            response = self.paginator.process_response(self.send(url, "get"))
            raw_resources += self.client.get_response_data(response, self.Meta.parse_json)[self.json_collection_attribute] if self.json_collection_attribute is not None else self.client.get_response_data(response, self.Meta.parse_json)

        resources = []

        for raw_resource in raw_resources:
            try:
                resource = GrantedOauthApp(self.client)
            except (ValueError, TypeError):
                continue
            else:
                resource.update_from_dict(raw_resource)
                resources.append(resource)

        return resources
