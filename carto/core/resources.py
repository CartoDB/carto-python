import requests
from gettext import gettext as _
from urlparse import urljoin

from carto.core import CartoException


class APIConnected(object):
    collection_endpoint = ""

    def __init__(self, client):
        """
        :param client: Client to make authorized requests
        :return:
        """
        self.client = client

    def get_resource_endpoint(self, resource_id):
        return urljoin(self.collection_endpoint, resource_id)

    def send(self, url, http_method="GET", **client_args):
        """
        Make the actual request to the API
        :param url: URL
        :param http_method: The method used to make the request to the API
        :param client_args: Arguments to be sent to the auth client
        :return: requests' response object
        """
        return self.client.send(url, http_method=http_method, **client_args)


class Resource(APIConnected):
    """
    Resource
    """
    _id = None
    fields = None
    id_field = "id"

    def __str__(self):
        return self._id if self._id is not None else super(Resource, self).__str__()

    @property
    def resource_endpoint(self):
        return self.get_resource_endpoint(self._id) if self._id is not None else None

    def update_from_dict(self, attribute_dict):
        """
        :param data_dict: Dictionary to be mapped into object attributes
        :return:
        """
        for field_name, field_value in attribute_dict.items():
            if self.fields is None or field_name in self.fields:
                setattr(self, field_name, field_value)
                if field_name == self.id_field:
                    self._id = field_value

    def send(self, url, http_method="GET", **client_args):
        """
        Make the actual request to the API
        :param url: Endpoint URL
        :param http_method: The method used to make the request to the API
        :param http_header: The header used to make write requests to the API, by default is none
        :param file_body: The information in the json file needed to create the named map
        :return:
        """
        response = super(Resource, self).send(url, http_method=http_method, **client_args)

        # Update Python object if we get back a full object from the API
        if response.status_code == requests.codes.ok or response.status_code == requests.codes.created:
            try:
                self.update_from_dict(self.client.get_response_data(response))
            except ValueError:
                pass

        return response.status_code

    def save(self):
        """
        Creates a new named map in the CARTO server
        :return:

        reconstruct json based on object parameters
        """
        values = {field_name: getattr(self, field_name) for field_name in self.fields if hasattr(self, field_name)}

        if self.resource_endpoint is not None:
            status_code = self.send(self.resource_endpoint, "PUT", http_headers={'content-type': 'application/json'}, json=values)
            if status_code == requests.codes.not_found:
                raise CartoException(_("Object not found (HTTP error code: {error_code})".format(error_code=status_code)))
            elif status_code != requests.codes.ok:
                raise CartoException(_("Object could not be modified (HTTP error code: {error_code})".format(error_code=status_code)))
        else:
            status_code = self.send(self.collection_endpoint, "POST", http_headers={'content-type': 'application/json'}, json=values)
            if status_code != requests.codes.created and status_code != requests.codes.ok:  # API_ISSUE: Many times sucessful POST requests are acknowledged by a 200 OK
                raise CartoException(_("Object could not be created (HTTP error code: {error_code})".format(error_code=status_code)))

    def refresh(self):
        """
        Refreshes a resource by checking against the API
        """
        if self.resource_endpoint is not None:
            status_code = self.send(self.resource_endpoint)
            if status_code != requests.codes.ok:
                raise CartoException(_("Object could not be refreshed"))

    def delete(self):
        """
        Deletes the model from the user account in CARTO; Python object remains untouched
        :return: A status code depending on whether the delete request was successful
        """
        if self.resource_endpoint is not None:
            status_code = self.send(self.resource_endpoint, http_method="DELETE")
            if status_code == requests.codes.not_found:
                raise CartoException(_("Object not found (HTTP error code: {error_code})".format(error_code=status_code)))
            elif status_code != requests.codes.no_content and status_code != requests.codes.ok:  # API_ISSUE: Many times sucessful DELETE requests are acknowledged by a 200 OK
                raise CartoException(_("Object could not be deleted (HTTP error code: {error_code})".format(error_code=status_code)))

            self._id = None


class AsyncResource(Resource):
    def run(self, **client_params):
        """
        Actually creates the async job on the CARTO server
        :param import_params: To be send to the Import API, see CARTO's docs on Import API for an updated list of accepted params
        :return:
        """
        status_code = self.send(self.collection_endpoint, http_method="POST", **client_params)
        if status_code != requests.codes.created and status_code != requests.codes.ok:  # API_ISSUE: Many times sucessful POST requests are acknowledged by a 200 OK
            raise CartoException(_("Object could not be created (HTTP error code: {error_code})".format(error_code=status_code)))

    def refresh(self):
        """
        Updates the information of the async job against the CARTO server
        :return:
        """
        if self.resource_endpoint is None:
            raise CartoException("Async job needs to be run or retrieved first!")

        self.send(self.resource_endpoint)


class Manager(APIConnected):
    model_class = None
    json_collection_attribute = "data"
    json_resource_attribute = None

    def get(self, resource_id):
        """
        Get one named map or a list with all the current ones
        :param resource_id: Id of the resource to be retrieved
        :return: Retrieved resource
        """
        data = self.send(self.get_resource_endpoint(resource_id))

        if data.status_code == requests.codes.not_found:
            return None
        elif data.status_code != requests.codes.ok:
            raise CartoException(_("Could not retrieve resource (HTTP error code: {error_code})".format(error_code=data.status_code)))

        try:
            resource = self.model_class(self.client)
        except (ValueError, TypeError):
            return None
        else:
            if self.json_resource_attribute is None:
                resource.update_from_dict(data.json())
            else:
                resource.update_from_dict(data.json()[self.json_resource_attribute])
            return resource

    def all(self):
        """
        Get all the current named map
        :return: A list of resources
        """
        data = self.send(self.collection_endpoint)

        if data.status_code != requests.codes.ok:
            raise CartoException(_("Could not retrieve collection (HTTP error code: {error_code})".format(error_code=data.status_code)))

        resources = []

        for json_resource in data.json()[self.json_collection_attribute]:
            try:
                resource = self.model_class(self.client)
            except (ValueError, TypeError):
                continue
            else:
                if self.json_resource_attribute is None:
                    resource.update_from_dict(json_resource)
                else:
                    resource.update_from_dict(json_resource[self.json_resource_attribute])
                resources.append(resource)

        return resources

    def create(self, *args, **kwargs):
        resource = self.model_class(self.client, *args)
        resource.update_from_dict(kwargs)
        resource.save()

        return resource
