"""
Module for working with CARTO Auth API

https://carto.com/developers/auth-api/

.. module:: carto.api_keys
   :platform: Unix, Windows
   :synopsis: Module for working with CARTO Auth API

.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from pyrestcli.fields import CharField, DateTimeField

from .fields import TableGrantField, GrantsField
from .resources import Resource, Manager
from .exceptions import CartoException
from .paginators import CartoPaginator


API_VERSION = "v3"
API_ENDPOINT = "api/{api_version}/api_keys/"

API_SQL = "sql"
API_MAPS = "maps"
PERMISSION_INSERT = "insert"
PERMISSION_SELECT = "select"
PERMISSION_UPDATE = "update"
PERMISSION_DELETE = "delete"
SERVICE_GEOCODING = "geocoding"
SERVICE_ROUTING = "routing"
SERVICE_ISOLINES = "isolines"
SERVICE_OBSERVATORY = "observatory"


class APIKey(Resource):
    """
    Represents an API key in CARTO. API keys are used to grant permissions to
    tables and maps. See the Auth API reference for more info: https://carto.com/developers/auth-api/

    """
    name = CharField()
    token = CharField()
    type = CharField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    grants = GrantsField()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "name"

    def regenerate_token(self):
        """
        Regenerates the associated token

        :return:

        :raise: CartoException
        """
        try:
            endpoint = (self.Meta.collection_endpoint
                        + "{name}/token/regenerate"). \
                format(name=self.name)

            self.send(endpoint, "POST")
        except Exception as e:
            raise CartoException(e)


class APIKeyManager(Manager):
    """
    Manager for the APIKey class.

    """
    resource_class = APIKey
    json_collection_attribute = "result"
    paginator_class = CartoPaginator

    def create(self, name, apis=['sql', 'maps'], tables=None, services=None):
        """
        Creates a regular APIKey.

        :param name: The API key name
        :param apis: Describes which APIs does this API Key provide access to
        :param tables: Describes to which tables and which privleges on each table this API Key grants access to
        :param services: Describes to which data services this API Key grants access to
        :type name: str
        :type apis: list
        :type tables: TableGrant or dict
        :type services: list

        :return: An APIKey instance with a token
        """
        grants = []
        if not apis:
            raise CartoException("'apis' cannot be empty. Please specify which CARTO APIs you want to grant. Example: ['sql', 'maps']")
        grants.append({'type': 'apis', 'apis': apis})
        if tables and (len(tables) > 0):
            if isinstance(tables[0], dict):
                grants.append({'type': 'database', 'tables': tables})
            elif isinstance(tables[0], TableGrant):
                grants.append({'type': 'database', 'tables': [x.to_json for x in tables]})
        if services:
            grants.append({'type': 'dataservices', 'services': services})
        return super(APIKeyManager, self).create(name=name, grants=grants)


class TableGrant(Resource):
    """
    Describes to which tables and which privleges on each table this API Key grants access to trough tables attribute.
    This is an internal data type, with no specific API endpoints

    See https://carto.com/developers/auth-api/reference/#section/API-Key-format

    Example:

        .. code::

            {
                "type": "database",
                "tables": [
                    {
                        "schema": "public",
                        "name": "my_table",
                        "permissions": [
                            "insert",
                            "select",
                            "update"
                        ]
                    }
                ]
            }
    """
    schema = CharField()
    name = CharField()
    permissions = CharField(many=True)

    def to_json(self):
        return {
                'schema': self.schema,
                'name': self.name,
                'permissions': self.permissions
            }


class Grants(Resource):
    apis = CharField(many=True)
    tables = TableGrantField(many=True)
    services = CharField(many=True)

    def get_id(self):
        tables = []
        if self.tables:
            tables = [x.to_json() for x in self.tables]
        return [
                    {
                        'type': 'apis',
                        'apis': self.apis or []
                    },
                    {
                        'type': 'database',
                        'tables': tables
                    },
                    {
                        'type': 'dataservices',
                        'services': self.services or []
                    }
                ]
