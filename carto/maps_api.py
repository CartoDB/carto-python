import json


MAPS_API_URL = '{api_version}/map/named/'


class NamedMap(object):
    """
    Equivalent to creating a named map in CARTO.
    """
    version = '0.0.1'

    def __init__(self, client, params=None, api_version='v1'):
        """
        :param client: Client to make authorized requests
        :param template_name: The name of the json file with all of the information about the named map
        :param api_version: Current version is 'v1. Others are not guaranteed to work
        :param is_file: Is by default true when creating a NamedMap, and set to false when using NamedMapMananger
        :param template_id: Is used to identify the map. Is only necessary whn using NamedMapMananger
        :return:
        """
        self.client = client
        self.api_url = MAPS_API_URL.format(api_version=api_version)
        self.update_from_dict(params)

    def update_from_dict(self, data_dict):
        """
        :param data_dict: Dictionary to be mapped into object attributes
        :return:
        """
        for k, v in data_dict.items():
            setattr(self, k, v)
        if "item_queue_id" in data_dict:
            self.id = data_dict["item_queue_id"]

    def send(self, url, http_method, http_header=None, file_body=None):
        """
        Make the actual request to the Maps API
        :param url: Endpoint URL
        :param http_method: The method used to make the request to the API
        :param http_header: The header used to make write requests to the API, by default is none
        :param file_body: The information in the json file needed to create the named map
        :return:
        """
        data = self.client.send(url, http_method=http_method, http_headers=http_header, body=file_body)
        data_json = self.client.get_response_data(data)
        self.update_from_dict(data_json)

    def save(self):
        """
        Creates a new named map in the CARTO server
        :return:

        reconstruct json based on object parameters
        """
        header = {'content-type': 'application/json'}

        if self.version == '0.0.1':
            attrs = ["version", "name", "auth", "placeholders", "layergroup", "view"]
        else:
            attrs = [key for key in self.__dict__.keys() if not key.startswith('__')]
            try:
                attrs.remove('client')
            except ValueError:
                pass
            try:
                attrs.remove('api_url')
            except ValueError:
                pass

        vals = []
        for a in attrs:
            vals += [getattr(self, a, None)]
        attr_dict = {}
        for i in range(len(attrs)):
            attr_dict[attrs[i]] = vals[i]
        template_json = json.dumps(attr_dict)

        if hasattr(self, 'template_id'):
            self.send(self.api_url + self.template_id, "PUT", header, template_json)
        else:
            self.send(self.api_url, "POST", header, template_json)

    def instantiate(self, params, auth=None):
        """
        Allows you to fetch the map tiles of a created map
        :param params_name: The json with the styling info for the named map
        :return:
        """
        header = {'content-type': 'application/json'}
        params_json = json.dumps(params)
        if (auth is not None):
            self.send(self.api_url + self.template_id + "?auth_token=" + auth, "POST", header, params_json)
        else:
            self.send(self.api_url + self.template_id, "POST", header, params_json)

    def delete(self):
        """
        Deletes the named map from the user account in CARTO
        :return: A status code depending on whether the delete request was successful
        """
        check = self.client.send(self.api_url + self.template_id, http_method="DELETE")
        return check.status_code


class NamedMapManager(object):
    def __init__(self, client, api_version='v1'):
        """
        :param client: Client to make authorized requests
        :param api_version: Current version is 'v1. Others are not guaranteed to work
        :return:
        """
        self.client = client
        self.api_url = MAPS_API_URL.format(api_version=api_version)

    def get(self, id=None, ids_only=False):
        """
        Get one named map or a list with all the current ones
        :param id: If set, only this map will be retrieved. This works no matter the state of the map
        :param ids_only: If True, a list of IDs is returned; if False, a list of NamedMap objects is returned
        :return: An named map, a list of named map IDs or a list of named maps
        """
        if id is not None:
            data = self.client.send(self.api_url + id)
            try:
                return NamedMap(self.client, data.json()['template'])
            except ValueError:
                return None
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
        """
        Get all the current named map
        :param ids_only: If True, a list of IDs is returned; if False, a list of NamedMap objects is returned
        :return: A list of named map IDs or a list of named maps
        """
        return self.get(ids_only=ids_only)
