"""
Module for working with CARTO datasets

.. module:: carto.datasets
   :platform: Unix, Windows
   :synopsis: Module for working with CARTO datasets

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

import time
import json
from gettext import gettext as _

from pyrestcli.fields import IntegerField, CharField, DateTimeField, \
    BooleanField

from .exceptions import CartoException
from .file_import import FileImportJobManager
from .resources import WarnResource
from .sync_tables import SyncTableJobManager
from .tables import TableManager
from .fields import TableField, UserField, PermissionField
from .paginators import CartoPaginator
from .resources import Manager


API_VERSION = "v1"
API_ENDPOINT = "api/{api_version}/viz/"

MAX_NUMBER_OF_RETRIES = 60
INTERVAL_BETWEEN_RETRIES_S = 10


class Dataset(WarnResource):
    """
    Represents a dataset in CARTO. Typically, that means there is a table in
    the PostgreSQL server associated to this object.

    .. warning:: Non-public API. It may change with no previous notice
    """
    active_child = None
    active_layer_id = CharField()
    attributions = None
    auth_tokens = CharField(many=True)
    children = None
    created_at = DateTimeField()
    connector = None
    description = CharField()
    display_name = CharField()
    external_source = None
    id = CharField()
    kind = CharField()
    license = None
    liked = BooleanField()
    likes = IntegerField()
    locked = BooleanField()
    map_id = CharField()
    name = CharField()
    next_id = None
    parent_id = CharField()
    permission = PermissionField()
    prev_id = None
    privacy = CharField()
    source = None
    stats = DateTimeField(many=True)
    synchronization = None
    table = TableField()
    tags = CharField(many=True)
    title = CharField()
    transition_options = None
    type = CharField()
    updated_at = DateTimeField()
    url = CharField()
    uses_builder_features = BooleanField()
    user = UserField()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "name"


class DatasetManager(Manager):
    """
    Manager for the Dataset class.

    .. warning:: Non-public API. It may change with no previous notice
    """
    resource_class = Dataset
    json_collection_attribute = "visualizations"
    paginator_class = CartoPaginator

    def send(self, url, http_method, **client_args):
        """
        Sends an API request, taking into account that datasets are part of
        the visualization endpoint.

        :param url: Endpoint URL
        :param http_method: The method used to make the request to the API
        :param client_args: Arguments to be sent to the auth client
        :type url: str
        :type http_method: str
        :type client_args: kwargs

        :return: A request response object

        :raise: CartoException
        """
        try:
            client_args = client_args or {}

            if "params" not in client_args:
                client_args["params"] = {}
            client_args["params"].update({"type": "table",
                                          "exclude_shared": "true"})

            return super(DatasetManager, self).send(url,
                                                    http_method,
                                                    **client_args)
        except Exception as e:
            raise CartoException(e)

    def is_sync_table(self, archive, interval, **import_args):
        """
        Checks if this is a request for a sync dataset.

        The condition for creating a sync dataset is to provide a URL or a
        connection to an external database and an interval in seconds

        :param archive: URL to the file (both remote URLs or local paths are
                    supported) or StringIO object
        :param interval: Interval in seconds.
        :param import_args: Connection parameters for an external database
        :type url: str
        :type interval: int
        :type import_args: kwargs

        :return: True if it is a sync dataset

        """
        return (hasattr(archive, "startswith") and archive.startswith("http")
                or "connection" in import_args) \
            and interval is not None

    def create(self, archive, interval=None, **import_args):
        """
        Creating a table means uploading a file or setting up a sync table

        :param archive: URL to the file (both remote URLs or local paths are
                    supported) or StringIO object
        :param interval: Interval in seconds.
                        If not None, CARTO will try to set up a sync table
                        against the (remote) URL
        :param import_args: Arguments to be sent to the import job when run
        :type archive: str
        :type interval: int
        :type import_args: kwargs

        :return: New dataset object
        :rtype: Dataset

        :raise: CartoException
        """
        archive = archive.lower() if hasattr(archive, "lower") else archive

        if self.is_sync_table(archive, interval, **import_args):
            manager = SyncTableJobManager(self.client)
        else:
            manager = FileImportJobManager(self.client)

        import_job = manager.create(archive) if interval is None \
            else manager.create(archive, interval)
        import_job.run(**import_args)

        if import_job.get_id() is None:
            raise CartoException(_("Import API returned corrupt job details \
                                   when creating dataset"))

        import_job.refresh()

        count = 0
        while import_job.state in ("enqueued", "pending", "uploading",
                                   "unpacking", "importing", "guessing") \
            or (isinstance(manager, SyncTableJobManager)
                and import_job.state == "created"):
            if count >= MAX_NUMBER_OF_RETRIES:
                raise CartoException(_("Maximum number of retries exceeded \
                                       when polling the import API for \
                                       dataset creation"))
            time.sleep(INTERVAL_BETWEEN_RETRIES_S)
            import_job.refresh()
            count += 1

        if import_job.state == "failure":
            raise CartoException(_("Dataset creation was not successful \
                                   because of failed import (error: {error}")
                                 .format(error=json.dumps(
                                     import_job.get_error_text)))

        if (import_job.state != "complete" and import_job.state != "created"
            and import_job.state != "success") \
                or import_job.success is False:
            raise CartoException(_("Dataset creation was not successful \
                                   because of unknown import error"))

        if hasattr(import_job, "visualization_id") \
                and import_job.visualization_id is not None:
            visualization_id = import_job.visualization_id
        else:
            table = TableManager(self.client).get(import_job.table_id)
            visualization_id = table.table_visualization.get_id() \
                if table is not None else None

        try:
            return self.get(visualization_id) if visualization_id is not None \
                else None
        except AttributeError:
            raise CartoException(_("Dataset creation was not successful \
                                   because of unknown error"))
