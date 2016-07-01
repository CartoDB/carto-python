from .core import CartoException
from secret import API_KEY, USER, EXISTING_TABLE, IMPORT_FILE, IMPORT_URL

import requests


IMPORT_API_FILE_URL = 'v1/map/named/'


class NamedMap(object):

	def __init__(self, client, template_name, params_name):
		self.client = client
		self.template_name = template_name
		self.params_name = params_name

	def update_from_dict(self, data_dict):
		for k, v in data_dict.items():  
			setattr(self, k, v)
		if "item_queue_id" in data_dict:
			self.id = data_dict["item_queue_id"]

	def send(self, url, h_method, http_header=None, file_body=None):
		data = self.client.send(url, http_method=h_method, http_headers=http_header, body=file_body)
		data_json = self.client.get_response_data(data)
		self.update_from_dict(data_json)

	def create(self):
		header = {'content-type': 'application/json'}
		payload = open(self.template_name)
		self.send(IMPORT_API_FILE_URL, "POST", header, payload)

	def instantiate(self, auth=None):
		header = {'content-type': 'application/json'}
		payload = open(self.params_name)
		if (auth != None): 
			self.send(IMPORT_API_FILE_URL+self.template_id+"?auth_token="+auth, "POST", header, payload)
		else:
			self.send(IMPORT_API_FILE_URL+self.template_id, "POST", header, payload)

	def update(self):
		header = {'content-type': 'application/json'}
		payload = open(self.template_name)
		self.send(IMPORT_API_FILE_URL+self.template_id, "PUT", header, payload)

	def delete(self):
		check = self.client.send(IMPORT_API_FILE_URL+self.template_id, http_method="DELETE")
		return check.status_code


class NamedMapManager(object):
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

