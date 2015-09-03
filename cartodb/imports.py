from cartodb import CartoDBException


class ImportJob(object):
    """
    Equivalent to a job process on CartoDB.
    New jobs have no id until they're "run". Then, they can be updated so that their attributes
    reflect the current status of the job.
    """
    id = None

    def __init__(self, client, type_guessing=True, quoted_fields_guessing=True, content_guessing=False, create_vis=False, **kwargs):
        """
        :param client: Client to make authorized requests (currently only CartoDBAPIKey is supported)
        :param type_guessing: If set to False disables field type guessing (for Excel and CSVs)
        :param quoted_fields_guessing: If set to False disables type guessing of CSV fields that come inside double quotes
        :param content_guessing: Set it to True to enable content guessing and automatic geocoding based on results. Currently it only implemenents geocoding of countries.
        :param create_vis: Set it to true to flag the import so when it finishes, it creates automatically Map after importing the Dataset
        :param kwargs: Dictionary with the data attributes that come from the Import API response. They will be mapped to real object attributes.
        :return:
        """
        self.client = client
        self.run_params = {"type_guessing": type_guessing,
                           "quoted_fields_guessing": quoted_fields_guessing,
                           "content_guessing": content_guessing,
                           "create_vis": create_vis}

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

    def req(self, url, api_params=None, client_params=None):
        """
        Make the actual request to the Import API
        :param url: Endpoint URL
        :param api_params: Params to be appended to the URL
        :param client_params: Params to be sent to the client (and, in turn, to requests)
        :return:
        """
        resp = self.client.req(url, params=api_params, **client_params or {})
        response_data = self.client.get_response_data(resp, True)
        self.update_from_dict(response_data)

    def run(self):
        """
        Creates the job import on the CartoDB server, must be implemented by children classes
        """
        raise NotImplementedError

    def update(self):
        """
        Updates the information of the import job against the CartoDB server
        :return:
        """
        if self.id is None:
            raise CartoDBException("Import job needs to be run first!")

        self.req("%s/%s" % (self.client.imports_url, self.id))


class FileImport(ImportJob):
    """
    This class provides support for uploading and importing local files into CartoDB
    """
    def __init__(self, file_name, *args, **kwargs):
        """
        :param file_name: File name (paths are supported)
        :param args: Sent to parent class
        :param kwargs: Sent to parent class
        :return:
        """
        super(FileImport, self).__init__(*args, **kwargs)
        self.files = {'file': open(file_name, 'rb')}

    def run(self):
        """
        Actually creates the job import on the CartoDB server
        :return:
        """
        self.req(self.client.imports_url, api_params=self.run_params, client_params={"files": self.files, "http_method": "POST"})


class URLImport(ImportJob):
    """
    This class provides support for uploading and importing remote files into CartoDB
    No sync support yet
    """
    def __init__(self, url, *args, **kwargs):
        """
        :param url: Remote URL for the file
        :param args: Sent to parent class
        :param kwargs: Sent to parent class
        :return:
        """
        super(URLImport, self).__init__(*args, **kwargs)
        self.url = url

    def run(self):
        """
        Actually creates the job import on the CartoDB server
        :return:
        """
        api_params = self.run_params
        api_params["url"] = self.url

        self.req(self.client.imports_url, api_params=api_params, client_params={"http_method": "POST"})


class ImportManager(object):
    item_queue_id = None

    def __init__(self, client):
        """
        :param client: Client to make authorized requests (currently only CartoDBAPIKey is supported)
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
            resp = self.client.req("%s/%s" % (self.client.imports_url, id))
            response_data = self.client.get_response_data(resp, True)
            return ImportJob(self.client, **response_data)
        else:
            imports = []

            resp = self.client.req(self.client.imports_url)
            response_data = self.client.get_response_data(resp, True)
            if response_data["success"] is True:
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
