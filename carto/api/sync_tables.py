from carto.core import AsyncResource, Manager


API_VERSION = "v1"
API_ENDPOINT = '{api_version}/synchronizations'


class SyncTableJob(AsyncResource):
    """
    This class provides support for creating Sync Tables into CARTO
    """
    collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)

    def __init__(self, client, url, interval):
        """
        :param url: Remote URL for the file
        :param client: Client to make authorized requests (currently only APIKeyAuthClient is supported)
        :param interval: Number of seconds between update intervals (>=900)
        :return:
        """
        self.url = url
        self.interval = interval

        super(SyncTableJob, self).__init__(client)

    def run(self, **import_params):
        """
        Actually creates the job import on the CARTO server
        :param import_params: To be send to the Import API, see CARTO's docs on Import API for an updated list of accepted params
        :return:
        """
        import_params["url"] = self.url
        import_params["interval"] = self.interval

        return super(SyncTableJob, self).run(params=import_params)


class SyncTableJobManager(Manager):
    model_class = SyncTableJob
    json_collection_attribute = "synchronizations"
    collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
