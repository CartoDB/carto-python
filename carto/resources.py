"""
Extensions for pyrestcli Resource and Manager classes

.. module:: carto.resources
   :platform: Unix, Windows
   :synopsis: Extensions for pyrestcli Resource and Manager classes

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <daniel@carto.com>


"""
from pyrestcli.resources import Resource, Manager as PyRestCliManager

from .exceptions import CartoException


class AsyncResource(Resource):
    def run(self, **client_params):
        """
        Actually creates the async job on the CARTO server


        :param client_params: To be send to the CARTO API. See CARTO's documentation depending on the subclass you are using
        :type client_params: kwargs


        :return:
        :raise: CartoException
        """
        try:
            self.send(self.get_collection_endpoint(), http_method="POST", **client_params)
        except Exception as e:
            raise CartoException(e)

    def refresh(self):
        """
        Updates the information of the async job against the CARTO server. After calling the :func:`refresh` method you should check the `state` attribute of your resource


        :return:
        """
        if self.get_resource_endpoint() is None:
            raise CartoException("Async job needs to be run or retrieved first!")

        super(AsyncResource, self).refresh()


class Manager(PyRestCliManager):
    """
    Manager class for resources
    """
    def __init__(self, auth_client):
        """
        :param auth_client: Client to make (non)authorized requests

        :return:
        """
        self.paginator = self.paginator_class(self.json_collection_attribute, auth_client.base_url)
        super(PyRestCliManager, self).__init__(auth_client)
