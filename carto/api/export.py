from carto.core import AsyncResource


API_VERSION = "v3"
API_ENDPOINT = '{api_version}/visualization_exports/'


class ExportJob(AsyncResource):
    """
    Equivalent to a carto export in CARTO.
    Allows a carto export to be created using a visualization in the user's CARTO account
    """
    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)

    def __init__(self, client, visualization_id):
        """
        :param client: Client to make authorized requests
        :param visualization_id: The id of the visualization (or dataset!!!) that will be exported
        :return:
        """
        self.visualization_id = visualization_id

        super(ExportJob, self).__init__(client)

    def run(self, **export_params):
        """
        Make the actual request to the Import API
        :param import_params: Any additional parameters
        :return:
        """
        export_params["visualization_id"] = self.visualization_id

        return super(ExportJob, self).run(params=export_params)
