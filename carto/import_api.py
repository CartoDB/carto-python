from .core import CartoException


IMPORT_API_FILE_URL = '{api_version}/imports'
IMPORT_API_SYNC_TABLE_URL = '{api_version}/synchronizations'


class ImportJob(object):
    """
    Equivalent to a job process on CartoDB.
    New jobs have no id until they're "run". Then, they can be updated so that their attributes
    reflect the current status of the job.
    """
    id = None
    api_url = None
    files = None
    url = None
    interval = None

    def __init__(self, client, **kwargs):
        """
        :param client: Client to make authorized requests (currently only APIKeyAuthClient is supported)
        :param kwargs: Dictionary with the data attributes of existing jobs that come from the Import API response.
                       They will be mapped to real object attributes.
        :return:
        """
        self.client = client
        self.update_from_dict(kwargs)

    def update_from_dict(self, data_dict):
        """
        :param data_dict: Dictionary to be mapped into object attributes
        :return:
        """
        for k, v in data_dict.items():  # More efficient if use 'future.utils.iteritems' or 'six.iteritems'
            setattr(self, k, v)
        if "item_queue_id" in data_dict:
            self.id = data_dict["item_queue_id"]

    def send(self, url, url_params=None, client_params=None):
        """
        Make the actual request to the Import API
        :param url: Endpoint URL
        :param url_params: Params to be appended to the URL
        :param client_params: Params to be sent to the client (and, in turn, to requests)
        :return:
        """
        resp = self.client.send(url, params=url_params, **client_params or {})
        response_data = self.client.get_response_data(resp, True)
        self.update_from_dict(response_data)

    def run(self, **import_params):
        """
        Actually creates the job import on the CartoDB server
        :param import_params: To be send to the Import API, see Carto's docs on Import API for an updated list of accepted params
        :return:
        """
        if self.url is not None:  # URL import
            import_params["url"] = self.url
            if self.interval is not None:  # Sync table
                import_params["interval"] = self.interval
            self.send(self.api_url, client_params={"json": import_params, "http_method": "POST"})
        elif self.files is not None:  # File import
            self.send(self.api_url, url_params=import_params, client_params={"http_method": "POST", "files": self.files})

    def update(self):
        """
        Updates the information of the import job against the CartoDB server
        :return:
        """
        if self.id is None:
            raise CartoException("Import job needs to be run or retrieved first!")

        self.send("%s/%s" % (self.api_url, self.id))


class FileImport(ImportJob):
    """
    This class provides support for uploading and importing local files into CartoDB
    """
    def __init__(self, file_name, client, api_version='v1', **kwargs):
        """
        :param file_name: File name (paths are supported)
        :param client: Client to make authorized requests (currently only APIKeyAuthClient is supported)
        :param api_version: Only 'v1' is currently supported
        :param kwargs: Sent to parent class
        :return:
        """
        self.files = {'file': open(file_name, 'rb')}
        self.api_url = IMPORT_API_FILE_URL.format(api_version=api_version)

        super(FileImport, self).__init__(client, **kwargs)


class URLImport(ImportJob):
    """
    This class provides support for uploading and importing remote files into CartoDB
    Sync tables are created if the interval param is used
    """
    def __init__(self, url, client, api_version='v1', interval=None, **kwargs):
        """
        :param url: Remote URL for the file
        :param client: Client to make authorized requests (currently only APIKeyAuthClient is supported)
        :param api_version: Only 'v1' is currently supported
        :param interval: Number of seconds between update intervals (>=900). If none, URL won't be sync'ed
        :param kwargs: Sent to parent class
        :return:
        """
        self.url = url
        self.interval = interval
        self.api_url = IMPORT_API_SYNC_TABLE_URL.format(api_version=api_version)

        super(URLImport, self).__init__(client, **kwargs)


class ImportManager(object):
    item_queue_id = None
    api_url = None

    def __init__(self, client):
        """
        :param client: Client to make authorized requests (currently only APIKeyAuthClient is supported)
        :return:
        """
        self.client = client

    def get(self, id=None, ids_only=False):
        """
        Get one import job or a list with all the current (pending) import jobs
        :param id: If set, only this job will be retrieved. This works no matter the state of the job
        :param ids_only: If True, a list of IDs is returned; if False, a list of ImportJob objects is returned
        :return: An import job, a list of import job IDs or a list of import jobs
        """
        if id is not None:
            resp = self.client.send("%s/%s" % (self.api_url, id))
            response_data = self.client.get_response_data(resp, True)
            return ImportJob(self.client, **response_data)
        else:
            imports = []

            resp = self.client.send(self.api_url)
            response_data = self.client.get_response_data(resp, True)
            if response_data.get("success", False) is not False:
                for import_job_id in response_data["imports"]:
                    if ids_only is True:
                        imports.append(import_job_id)
                    else:
                        imports.append(self.get(import_job_id))

            return imports

    def all(self, ids_only=False):
        """
        Get all the current (pending) import jobs
        :param ids_only: If True, a list of IDs is returned; if False, a list of ImportJob objects is returned
        :return: A list of import job IDs or a list of import jobs
        """
        return self.get(ids_only=ids_only)


class FileImportManager(ImportManager):

    def __init__(self, client, api_version='v1', **kwargs):
        """
        :param client: Client to make authorized requests (currently only APIKeyAuthClient is supported)
        :param api_version: Only 'v1' is currently supported
        :param kwargs: Sent to parent class
        :return:
        """
        self.api_url = IMPORT_API_FILE_URL.format(api_version=api_version)

        super(FileImportManager, self).__init__(client, **kwargs)


class URLImportManager(ImportManager):

    def __init__(self, client, api_version='v1', **kwargs):
        """
        :param client: Client to make authorized requests (currently only APIKeyAuthClient is supported)
        :param api_version: Only 'v1' is currently supported
        :param kwargs: Sent to parent class
        :return:
        """
        self.api_url = IMPORT_API_SYNC_TABLE_URL.format(api_version=api_version)

        super(URLImportManager, self).__init__(client, **kwargs)
