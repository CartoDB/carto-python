from pyrestcli.fields import ResourceField


class VisualizationField(ResourceField):
    value_class = "carto.visualizations.Visualization"


class TableField(ResourceField):
    value_class = "carto.tables.Table"


class UserField(ResourceField):
    value_class = "carto.users.User"


class EntityField(ResourceField):
    value_class = "carto.permissions.Entity"


class PermissionField(ResourceField):
    value_class = "carto.permissions.Permission"
