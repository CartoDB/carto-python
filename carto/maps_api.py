import requests


MAPS_API_URL = '{api_version}/map/named/'


class NamedMap(object):
    def __init__(self, client, template_name, params_name, api_version='v1'):
        self.client = client
        self.template_name = template_name
        self.params_name = params_name
        self.api_url = MAPS_API_URL.format(api_version=api_version)

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
        with open(self.template_name) as payload:
        	self.send(self.api_url, "POST", header, payload)

    def instantiate(self, auth=None):
        header = {'content-type': 'application/json'}
        with open(self.params_name) as payload:
	        if (auth is not None): 
	            self.send(self.api_url + self.template_id + "?auth_token=" + auth, "POST", header, payload)
	        else:
	            self.send(self.api_url + self.template_id, "POST", header, payload)

    def update(self):
        header = {'content-type': 'application/json'}
        with open(self.template_name) as payload:
        	self.send(self.api_url + self.template_id, "PUT", header, payload)

    def delete(self):
        check = self.client.send(self.api_url + self.template_id, http_method="DELETE")
        return check.status_code


class NamedMapManager(object):
    def __init__(self, client, api_version='v1'):
        self.client = client
        self.api_url = MAPS_API_URL.format(api_version=api_version)

    def get(self, id=None):
        if id is not None:
            data = self.client.send(self.api_url + id)
            return data.json()
        else:
            data = self.client.send(self.api_url)
            named_maps = data.json()['template_ids']
            return named_maps

    def all(self):
        return self.get()

