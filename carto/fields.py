"""
Module for defining response objects

.. module:: carto.fields
   :platform: Unix, Windows
   :synopsis: Module for defining response objects

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from pyrestcli.fields import ResourceField


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
