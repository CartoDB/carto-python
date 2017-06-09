"""
Module for the IMPORT API with sync tables

.. module:: carto.sync_tables
   :platform: Unix, Windows
   :synopsis: Module for the IMPORT API with sync tables

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from pyrestcli.fields import IntegerField, CharField, BooleanField, \
    DateTimeField

from .exceptions import CartoException
from .resources import AsyncResource, Manager
from .paginators import CartoPaginator


API_VERSION = "v1"
API_ENDPOINT = 'api/{api_version}/synchronizations/'
API_FORCE_SYNC_SUFFIX = 'sync_now'


class SyncTableJob(AsyncResource):
    """
    This class provides support for creating Sync Tables into CARTO
    """
    id = CharField()
    name = CharField()
    interval = IntegerField()
    url = CharField()
    state = CharField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    run_at = DateTimeField()
    retried_times = IntegerField()
    log_id = CharField()
    error_code = IntegerField()
    error_message = CharField()
    ran_at = DateTimeField()
    modified_at = DateTimeField()
    etag = CharField()
    checksum = CharField()
    user_id = CharField()
    service_name = CharField()
    service_item_id = CharField()
    success = BooleanField()
    type_guessing = BooleanField()
    quoted_fields_guessing = BooleanField()
    content_guessing = BooleanField()
    visualization_id = CharField()
    from_external_source = BooleanField()
    synchronization_id = CharField()
    enqueued = BooleanField()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)

    def __init__(self, url, interval, auth_client):
        """
        :param url: Remote URL for the file
        :param interval: Number of seconds between update intervals (>=900)
        :param client: Client to make authorized requests (currently only
                        APIKeyAuthClient is supported)
        :type url: str
        :type interval: int
        :type client: :class:`carto.auth.APIKeyAuthClient`

        :return:
        """
        self.url = url
        self.interval = interval

        super(SyncTableJob, self).__init__(auth_client)

    def run(self, **import_params):
        """
        Actually creates the job import on the CARTO server

        :param import_params: To be send to the Import API, see CARTO's docs
                                on Import API for an updated list of accepted
                                params
        :type import_params: kwargs

        :return:

        .. note:: The sync table job is asynchronous, so you should take care of the progression, by calling the :func:`carto.resources.AsyncResource.refresh` method and check the import job :py:attr:`~state` attribute. See :func:`carto.datasets.DatasetManager.create` for a unified method to import files into CARTO
        """
        import_params["url"] = self.url
        import_params["interval"] = self.interval

        if "connection" in import_params:
            self.fields.append("connector")
            import_params["connection"]["interval"] = self.interval
            self.update_from_dict(import_params["connection"])
            self.save(force_create=True)
        else:
            return super(SyncTableJob, self).run(params=import_params)

    def get_force_sync_endpoint(self):
        """
        Get the relative path to the specific API resource

        :return: Relative path to the resource

        :raise: CartoException
        """
        return urljoin(self.get_resource_endpoint(), API_FORCE_SYNC_SUFFIX)

    def force_sync(self):
        """
        Forces to sync the SyncTableJob

        :return:

        :raise: CartoException
        """
        try:
            self.send(self.get_resource_endpoint(), "put")
        except Exception as e:
            raise CartoException(e)


class SyncTableJobManager(Manager):
    """
    Manager for the SyncTableJob class
    """
    resource_class = SyncTableJob
    json_collection_attribute = "synchronizations"
    paginator_class = CartoPaginator

    def create(self, url, interval, **kwargs):
        """
        Create a sync table on the server

        :param url: URL can be a pointer to a remote location or a path to a
                    local file
        :param interval: Sync interval in seconds
        :param kwargs: Attributes (field names and values) of the new resource
        :type url: str
        :type interval: int
        :type kwargs: kwargs

        :return: SyncTableJob
        """
        resource = self.resource_class(url, interval, self.client)
        resource.update_from_dict(kwargs)
        resource.save(force_create=True)

        return resource
