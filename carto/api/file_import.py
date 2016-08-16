from carto.core import AsyncResource, Manager


API_VERSION = "v1"
API_ENDPOINT = '{api_version}/imports'


class FileImportJob(AsyncResource):
    """
    This class provides support for one-time uploading and importing of remote and local files into CARTO
    """
    collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)

    def __init__(self, url, client):
        """
        :param url: URL can be a pointer to a remote location or a path to a local file
        :param client: Client to make authorized requests (currently only APIKeyAuthClient is supported)
        :return:
        """
        if url.startswith("http"):
            self.url = url
            self.files = None
        else:
            self.url = None
            self.files = {'file': open(url, 'rb')}

        super(FileImportJob, self).__init__(client)

    def run(self, **import_params):
        """
        Actually creates the job import on the CARTO server
        :param import_params: To be send to the Import API, see CARTO's docs on Import API for an updated list of accepted params
        :return:
        """
        if self.url:
            import_params["url"] = self.url

        return super(FileImportJob, self).run(params=import_params, files=self.files)


class FileImportJobManager(Manager):
    model_class = FileImportJob
    json_collection_attribute = "imports"
    collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
