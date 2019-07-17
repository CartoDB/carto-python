"""
Module for working with CARTO Auth API

https://carto.com/developers/auth-api/

.. module:: carto.api_keys
   :platform: Unix, Windows
   :synopsis: Module for working with CARTO Auth API

.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from pyrestcli.fields import CharField, DateTimeField

from .fields import TableGrantField, GrantsField, SchemaGrantField
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
PERMISSION_DELETE = "create"
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

    def create(self, name, apis=['sql', 'maps'], tables=None, schemas=None, services=None):
        """
        Creates a regular APIKey.

        :param name: The API key name
        :param apis: Describes which APIs does this API Key provide access to
        :param tables: Describes to which tables and which privleges on each table this API Key grants access to
        :param schemas: Describes to which schemas and which privleges on each schema this API Key grants access to
        :param services: Describes to which data services this API Key grants access to
        :type name: str
        :type apis: list
        :type tables: TableGrant or dict
        :type schemas: SchemaGrant or dict
        :type services: list

        :return: An APIKey instance with a token
        """
        grants = []
        database_grant = {'type': 'database'}
        if not apis:
            raise CartoException("'apis' cannot be empty. Please specify which CARTO APIs you want to grant. Example: ['sql', 'maps']")
        grants.append({'type': 'apis', 'apis': apis})
        if tables and (len(tables) > 0):
            if isinstance(tables[0], dict):
                database_grant['tables'] = tables
            elif isinstance(tables[0], TableGrant):
                database_grant['tables'] = [x.to_json() for x in tables]
        if schemas and (len(schemas) > 0):
            if isinstance(schemas[0], dict):
                database_grant['schemas'] = schemas
            elif isinstance(schemas[0], SchemaGrant):
                database_grant['schemas'] = [x.to_json() for x in schemas]
        if services:
            grants.append({'type': 'dataservices', 'services': services})
        grants.append(database_grant)
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


class SchemaGrant(Resource):
    """
    Describes to which schemas and which privleges on each schema this API Key grants access to trough schemas attribute.
    For example if you grant `create` on the user `public` schema, they will be able to run `CREATE TABLE AS...` SQL queries
    This is an internal data type, with no specific API endpoints

    See https://carto.com/developers/auth-api/reference/#section/API-Key-format

    Example:

        .. code::

            {
                "type": "database",
                "schemas": [
                    {
                        "name": "public",
                        "permissions": [
                            "create"
                        ]
                    }
                ]
            }
    """
    name = CharField()
    permissions = CharField(many=True)

    def to_json(self):
        return {
                'name': self.name,
                'permissions': self.permissions
            }


class Grants(Resource):
    apis = CharField(many=True)
    tables = TableGrantField(many=True)
    services = CharField(many=True)
    schemas = SchemaGrantField(many=True)

    def get_id(self):
        tables = []
        schemas = []
        if self.tables:
            tables = [x.to_json() for x in self.tables]
        if self.schemas:
            schemas = [x.to_json() for x in self.schemas]
        return [
                    {
                        'type': 'apis',
                        'apis': self.apis or []
                    },
                    {
                        'type': 'database',
                        'tables': tables,
                        'schemas': schemas
                    },
                    {
                        'type': 'dataservices',
                        'services': self.services or []
                    }
                ]
