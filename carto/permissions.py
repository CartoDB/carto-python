"""
Entity classes for defining permissions

.. module:: carto.permissions
   :platform: Unix, Windows
   :synopsis: Entity classes for defining permissions

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from pyrestcli.resources import Resource
from pyrestcli.fields import CharField, DateTimeField

from .fields import UserField, EntityField


PUBLIC = "PUBLIC"
PRIVATE = "PRIVATE"
LINK = "LINK"


class Entity(Resource):
    """
    Represents an entity in CARTO. This is an internal data type, with no
    specific API endpoints
    """
    id = CharField()
    type = CharField()


class Permission(Resource):
    """
    Represents a permission in CARTO. This is an internal data type, with no
    specific API endpoints
    """
    acl = None
    created_at = DateTimeField()
    entity = EntityField()
    id = CharField()
    owner = UserField()
    updated_at = DateTimeField()
