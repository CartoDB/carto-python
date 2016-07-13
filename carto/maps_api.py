MAPS_API_URL = '{api_version}/map/named/'


class NamedMap(object):
    def __init__(self, client, template_name, api_version='v1', is_file=True, template_id=None):
        self.client = client
        self.template_name = template_name
        self.api_url = MAPS_API_URL.format(api_version=api_version)
        self.is_file = is_file
        self.template_id = template_id

    def update_from_dict(self, data_dict):
        for k, v in data_dict.items():
            setattr(self, k, v)
        if "item_queue_id" in data_dict:
            self.id = data_dict["item_queue_id"]

    def send(self, url, h_method, http_header=None, file_body=None):
        if self.is_file is True:
            data = self.client.send(url, http_method=h_method, http_headers=http_header, body=file_body)
        else:
            data = self.client.send(url, http_method=h_method, http_headers=http_header, json=file_body)
        data_json = self.client.get_response_data(data)
        self.update_from_dict(data_json)

    def create(self):
        header = {'content-type': 'application/json'}
        if self.is_file is True:
            with open(self.template_name) as payload:
                self.send(self.api_url, "POST", header, payload)
        else:
            self.send(self.api_url, "POST", header, self.template_name)

    def instantiate(self, params_name, auth=None):
        header = {'content-type': 'application/json'}
        with open(params_name) as payload:
            if (auth is not None):
                self.send(self.api_url + self.template_id + "?auth_token=" + auth, "POST", header, payload)
            else:
                self.send(self.api_url + self.template_id, "POST", header, payload)

    def update(self):
        header = {'content-type': 'application/json'}
        if self.is_file is True:
            with open(self.template_name) as payload:
                self.send(self.api_url + self.template_id, "PUT", header, payload)
        else:
            self.send(self.api_url + self.template_id, "PUT", header, self.template_name)

    def delete(self):
        check = self.client.send(self.api_url + self.template_id, http_method="DELETE")
        return check.status_code


class NamedMapManager(object):
    def __init__(self, client, api_version='v1'):
        self.client = client
        self.api_url = MAPS_API_URL.format(api_version=api_version)

    def get(self, id=None, ids_only=False):
        if id is not None:
            data = self.client.send(self.api_url + id)
            return NamedMap(self.client, data.json()['template'], is_file=False, template_id=id)
        else:
            named_maps = []

            data = self.client.send(self.api_url)
            named_maps_ids = data.json()['template_ids']
            for named_map_id in named_maps_ids:
                if ids_only is True:
                    named_maps.append(named_map_id)
                else:
                    named_maps.append(self.get(named_map_id))

            return named_maps

    def all(self, ids_only=False):
        return self.get(ids_only=ids_only)
