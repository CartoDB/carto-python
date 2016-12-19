from pyrestcli.resources import Resource, Manager as PyRestCliManager

from .exceptions import CartoException


class AsyncResource(Resource):
    def run(self, **client_params):
        """
        Actually creates the async job on the CARTO server
        :param import_params: To be send to the Import API, see CARTO's docs on Import API for an updated list of accepted params
        :return:
        """
        self.send(self.get_collection_endpoint(), http_method="POST", **client_params)

    def refresh(self):
        """
        Updates the information of the async job against the CARTO server
        :return:
        """
        if self.get_resource_endpoint() is None:
            raise CartoException("Async job needs to be run or retrieved first!")

        super(AsyncResource, self).refresh()


class Manager(PyRestCliManager):
    """
    Manager class for resources
    We need to pass the json_collection_attribute to the paginator
    """
    def __init__(self, auth_client):
        """
        :param auth_client: Client to make (non)authorized requests
        :return:
        """
        self.paginator = self.paginator_class(self.json_collection_attribute, auth_client.base_url)
        super(PyRestCliManager, self).__init__(auth_client)
