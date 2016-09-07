from pyrestcli.resources import Resource

from carto.core import CartoException


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
