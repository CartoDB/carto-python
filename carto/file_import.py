from carto.core import AsyncResource

from pyrestcli.resources import Manager
from pyrestcli.paginators import DummyPaginator  # Use CARTO's
from pyrestcli.fields import IntegerField, CharField, BooleanField

API_VERSION = "v1"
API_ENDPOINT = '{api_version}/imports/'


class FileImportJob(AsyncResource):
    """
    This class provides support for one-time uploading and importing of remote and local files into CARTO
    """
    item_queue_id = CharField()
    id = None
    user_id = None
    table_id = None
    data_type = None
    table_name = None
    state = None
    error_code = None
    queue_id = None
    tables_created_count = IntegerField()
    synchronization_id = None
    type_guessing = BooleanField()
    quoted_fields_guessing = None
    content_guessing = None
    create_visualization = None
    visualization_id = None
    user_defined_limits = None
    get_error_text = None
    display_name = None
    success = None
    warnings = None
    is_raster = None

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        id_field = "item_queue_id"

    def __init__(self, client, url):
        """
        :param client: Client to make authorized requests (currently only APIKeyAuthClient is supported)
        :param url: URL can be a pointer to a remote location or a path to a local file
        :return:
        """
        if url.startswith("http"):
            self.url = url
            self.files = None
        else:
            self.url = None
            self.files = {'file': open(url, 'rb')}

        super(FileImportJob, self).__init__(client)

    def run(self, **import_params):
        """
        Actually creates the job import on the CARTO server
        :param import_params: To be send to the Import API, see CARTO's docs on Import API for an updated list of accepted params
        :return:
        """
        if self.url:
            import_params["url"] = self.url

        super(FileImportJob, self).run(params=import_params, files=self.files)
        self.id_field = "id"


class FileImportJobManager(Manager):
    model_class = FileImportJob
    json_collection_attribute = "imports"
    paginator_class = DummyPaginator
