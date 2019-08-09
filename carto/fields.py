"""
Module for defining response objects

.. module:: carto.fields
   :platform: Unix, Windows
   :synopsis: Module for defining response objects

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

import base64

from pyrestcli.fields import ResourceField, CharField

PRIVACY_PUBLIC = 'public'
PRIVACY_PASSWORD = 'password'


class VisualizationField(ResourceField):
    """
    :class:`carto.visualizations.Visualization`
    """
    value_class = "carto.visualizations.Visualization"


class TableField(ResourceField):
    """
    :class:`carto.tables.Table`
    """
    value_class = "carto.tables.Table"


class UserField(ResourceField):
    """
    :class:`carto.users.User`
    """
    value_class = "carto.users.User"


class EntityField(ResourceField):
    """
    :class:`carto.permissions.Entity`
    """
    value_class = "carto.permissions.Entity"


class PermissionField(ResourceField):
    """
    :class:`carto.permissions.Permission`
    """
    value_class = "carto.permissions.Permission"


class SynchronizationField(ResourceField):
    """
    :class:`carto.synchronizations.Synchronization`
    """
    value_class = "carto.synchronizations.Synchronization"


class TableGrantField(ResourceField):
    """
    :class:`carto.api_keys.TableGrant`
    """
    value_class = "carto.api_keys.TableGrant"


class GrantsField(ResourceField):
    """
    :class:`carto.api_keys.Grants`
    """
    value_class = "carto.api_keys.Grants"
    type_field = {
        'apis': 'apis',
        'tables': 'database',
        'services': 'dataservices'
    }

    def __set__(self, instance, value):
        if self._initialized is False:
            self.set_real_value_class()

        resource = self.value_class(instance.client)
        for field in resource.fields:
            for grant_type in value:
                if grant_type['type'] == self.type_field[field]:
                    setattr(resource, field, grant_type[field])

        instance.__dict__[self.name] = resource


class Base64EncodedField(CharField):
    def __set__(self, instance, value):
        data = ""
        if value and isinstance(value, str):
            data = base64.b64encode(value.encode()).decode('ascii')

        super(Base64EncodedField, self).__set__(instance, data)


class PasswordAndPrivacyFields(CharField):
    def __set__(self, instance, value):
        password = None
        privacy = PRIVACY_PUBLIC

        if value and isinstance(value, str):
            password = value
            privacy = PRIVACY_PASSWORD

        super(PasswordAndPrivacyFields, self).__set__(instance, password)
        instance.__dict__['privacy'] = privacy
