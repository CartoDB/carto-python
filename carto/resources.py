"""
Extensions for pyrestcli Resource and Manager classes

.. module:: carto.resources
   :platform: Unix, Windows
   :synopsis: Extensions for pyrestcli Resource and Manager classes

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

import warnings

from pyrestcli.resources import Resource, Manager as PyRestCliManager

from .exceptions import CartoException


class AsyncResource(Resource):
    def run(self, **client_params):
        """
        Actually creates the async job on the CARTO server


        :param client_params: To be send to the CARTO API. See CARTO's
                                documentation depending on the subclass
                                you are using
        :type client_params: kwargs


        :return:
        :raise: CartoException
        """
        try:
            self.send(self.get_collection_endpoint(),
                      http_method="POST",
                      **client_params)
        except Exception as e:
            raise CartoException(e)

    def refresh(self):
        """
        Updates the information of the async job against the CARTO server.
        After calling the :func:`refresh` method you should check the `state`
        attribute of your resource

        :return:
        """
        if self.get_resource_endpoint() is None:
            raise CartoException("Async job needs to be run or retrieved \
                                 first!")

        super(AsyncResource, self).refresh()


class WarnAsyncResource(AsyncResource):
    """
    AsyncResource class for resources that represent non-public CARTO APIs.
    You'll be warned not to used the in production environments
    """
    def __init__(self, auth_client, **kwargs):
        """
        Initializes the resource
        :param auth_client: Client to make (non)authorized requests
        :param kwargs: Initial value for attributes
        :return:
        """

        warnings.warn('This is part of a non-public CARTO API and may change in \
              the future. Take this into account if you are using \
              this in a production environment', FutureWarning)
        super(WarnAsyncResource, self).__init__(auth_client, **kwargs)


class WarnResource(Resource):
    """
    Resource class for resources that represent non-public CARTO APIs.
    You'll be warned not to used the in production environments
    """
    def __init__(self, auth_client, **kwargs):
        """
        Initializes the resource
        :param auth_client: Client to make (non)authorized requests
        :param kwargs: Initial value for attributes
        :return:
        """

        warnings.warn('This is part of a non-public CARTO API and may change in the future. Take this into account if you are using this in a production environment', FutureWarning)
        super(WarnResource, self).__init__(auth_client, **kwargs)


class Manager(PyRestCliManager):
    """
    Manager class for resources
    """
    def __init__(self, auth_client):
        """
        :param auth_client: Client to make (non)authorized requests

        :return:
        """
        self.paginator = self.paginator_class(self.json_collection_attribute,
                                              auth_client.base_url)
        super(PyRestCliManager, self).__init__(auth_client)
