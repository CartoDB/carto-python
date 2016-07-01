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

	def __init__(self, client):
		self.client = client

	def get(self, id=None):
		if id is not None:
			header = {'content-type': 'application/json'}
			data = self.client.send(IMPORT_API_FILE_URL+id)
			return data.json()
		else:
			header = {'content-type': 'application/json'}
			data = self.client.send(IMPORT_API_FILE_URL)
			named_maps = data.json()['template_ids']
			return named_maps

	def all(self):
		return self.get()

