"""
Module for exporting visualizations

.. module:: carto.export
   :platform: Unix, Windows
   :synopsis: Module for exporting visualizations

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from pyrestcli.fields import CharField, DateTimeField

from .resources import WarnAsyncResource


API_VERSION = "v3"
API_ENDPOINT = 'api/{api_version}/visualization_exports/'


class ExportJob(WarnAsyncResource):
    """
    Equivalent to a .carto export in CARTO.

    Allows a CARTO export to be created using a visualization in the user's
    CARTO account

    .. warning:: Non-public API. It may change with no previous notice
    """
    id = CharField()
    visualization_id = CharField()
    user_id = CharField()
    state = CharField()
    url = CharField()
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)

    def __init__(self, client, visualization_id):
        """

        :param client: Client to make authorized requests
        :param visualization_id: The id of the visualization (or dataset!!!)
                                that will be exported
        :type client: :class:`carto.auth.APIKeyAuthClient`
        :type visualization_id: str

        :return:
        """

        self.visualization_id = visualization_id

        super(ExportJob, self).__init__(client)

    def run(self, **export_params):
        """
        Make the actual request to the Import API (exporting is part of the
        Import API).

        :param export_params: Any additional parameters to be sent to the
                                Import API
        :type export_params: kwargs

        :return:

        .. note:: The export is asynchronous, so you should take care of the progression, by calling the :func:`carto.resources.AsyncResource.refresh` method and check the export job :py:attr:`~state` attribute. See :func:`carto.visualizations.Visualization.export` method implementation for more details
        """
        export_params["visualization_id"] = self.visualization_id

        return super(ExportJob, self).run(params=export_params)
