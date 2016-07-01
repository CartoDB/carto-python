from .core import CartoException
from secret import API_KEY, USER, EXISTING_TABLE, IMPORT_FILE, IMPORT_URL

import requests


IMPORT_API_FILE_URL = 'v1/map/named'


class NamedMap(object):

	def __init__(self, client, template_name, params_name):
		self.client = client
		self.template_name = template_name
		self.params_name = params_name

	def create(self):
		header = {'content-type': 'application/json'}
		payload = open(self.template_name)
		data = requests.post('https://rsharan.cartodb.com/api/'+IMPORT_API_FILE_URL+"?api_key="+API_KEY, data=payload, headers=header)
		n_map_name = data.json()['template_id']
		return n_map_name

	def instantiate(self, map_name, auth=None):
		header = {'content-type': 'application/json'}
		payload = open(self.params_name)
		if (auth != None): 
			data = requests.post('https://rsharan.cartodb.com/api/v1/map/named/'+map_name+"?auth_token="+auth, data=payload, headers=header)
			print(data.json())
			return data.json()
		else:
			data = requests.post('https://rsharan.cartodb.com/api/v1/map/named/'+map_name, data=payload, headers=header)
			return data.json()

	def update(self, map_name):
		header = {'content-type': 'application/json'}
		payload = open(self.template_name)
		data = requests.put('https://rsharan.cartodb.com/api/v1/map/named/'+map_name+"?api_key="+API_KEY, data=payload, headers=header)
		print(data.json())
		return data.json()


	def delete(self, map_name):
		check = requests.delete('https://rsharan.cartodb.com/api/v1/map/named/'+map_name+"?api_key="+API_KEY)
		print(check.status_code)
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

