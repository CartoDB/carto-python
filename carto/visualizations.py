"""
Module for working with map visualizations

.. module:: carto.visualizations
   :platform: Unix, Windows
   :synopsis: Module for working with map visualizations

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

import time
from gettext import gettext as _

from pyrestcli.fields import IntegerField, CharField, DateTimeField, \
    BooleanField

from .exceptions import CartoException
from .fields import TableField
from .resources import Manager, WarnResource
from .paginators import CartoPaginator
from .export import ExportJob


API_VERSION = "v1"
API_ENDPOINT = "api/{api_version}/viz/"

MAX_NUMBER_OF_RETRIES = 30
INTERVAL_BETWEEN_RETRIES_S = 5


class Visualization(WarnResource):
    """
    Represents a map visualization in CARTO.

    .. warning:: Non-public API. It may change with no previous notice
    """
    active_child = None
    active_layer_id = CharField()
    attributions = None
    children = None
    created_at = DateTimeField()
    description = CharField()
    display_name = CharField()
    external_source = None
    id = CharField()
    kind = None
    license = None
    liked = BooleanField()
    likes = IntegerField()
    locked = BooleanField()
    map_id = CharField()
    name = CharField()
    next_id = None
    parent_id = None
    permission = None
    prev_id = None
    privacy = None
    source = None
    stats = None
    synchronization = None
    table = TableField()
    related_tables = TableField(many=True)
    tags = None
    title = CharField()
    transition_options = None
    type = None
    updated_at = DateTimeField()
    url = CharField()
    uses_builder_features = None

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "name"

    def export(self):
        """
        Make the actual request to the Import API (exporting is part of the
        Import API) to export a map visualization as a .carto file

        :return: A URL pointing to the .carto file
        :rtype: str

        :raise: CartoException

        .. warning:: Non-public API. It may change with no previous notice

        .. note:: The export is asynchronous, but this method waits for the export to complete. See `MAX_NUMBER_OF_RETRIES` and `INTERVAL_BETWEEN_RETRIES_S`
        """
        export_job = ExportJob(self.client, self.get_id())
        export_job.run()

        export_job.refresh()

        count = 0
        while export_job.state in ("exporting", "enqueued", "pending"):
            if count >= MAX_NUMBER_OF_RETRIES:
                raise CartoException(_("Maximum number of retries exceeded \
                                       when polling the import API for \
                                       visualization export"))
            time.sleep(INTERVAL_BETWEEN_RETRIES_S)
            export_job.refresh()
            count += 1

        if export_job.state == "failure":
            raise CartoException(_("Visualization export failed"))

        if (export_job.state != "complete" and export_job.state != "created"):
            raise CartoException(_("Unexpected problem on visualization export \
                                   (state: {state})").
                                 format(state=export_job.state))

        return export_job.url


class VisualizationManager(Manager):
    """
    Manager for the Visualization class.

    .. warning:: Non-public API. It may change with no previous notice
    """
    resource_class = Visualization
    json_collection_attribute = "visualizations"
    paginator_class = CartoPaginator

    def send(self, url, http_method, **client_args):
        """
        Sends API request, taking into account that visualizations are only a
        subset of the resources available at the visualization endpoint

        :param url: Endpoint URL
        :param http_method: The method used to make the request to the API
        :param client_args: Arguments to be sent to the auth client
        :type url: str
        :type http_method: str
        :type client_args: kwargs

        :return:

        :raise: CartoException
        """
        try:
            client_args.setdefault('params', {})
            client_args["params"].update({"type": "derived",
                                          "exclude_shared": "true"})

            return super(VisualizationManager, self).send(url,
                                                          http_method,
                                                          **client_args)
        except Exception as e:
            raise CartoException(e)

    def create(self, **kwargs):
        """
        Creating visualizations is better done by using the Maps API
        (named maps) or directly from your front end app if dealing with
        public datasets
        """
        pass
