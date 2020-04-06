import os
import time
import requests
from .utils import ResponseStream
from .exceptions import CartoException

VALID_TYPES = [
    'STRING', 'BYTES', 'INTEGER', 'INT64', 'FLOAT',
    'FLOAT64', 'BOOLEAN', 'BOOL', 'TIMESTAMP', 'DATE', 'TIME',
    'DATETIME', 'GEOMETRY'
]

TYPES_MAPPING = {
    'GEOMETRY': 'GEOGRAPHY'
}

DATASETS_BASE_PATH = 'api/v4/data/observatory/user/datasets'
ENRICHMENT_BASE_PATH = 'api/v4/data/observatory/enrichment'
METADATA_BASE_PATH = 'api/v4/data/observatory/metadata'


class _DODatasetClient:

    def __init__(self, auth_client):
        self.auth_client = auth_client
        self.api_key = getattr(self.auth_client, 'api_key', None)

    def upload(self, dataframe, name, params=None):
        params = params or {}
        dataframe.to_csv(path_or_buf=name, index=False)
        try:
            with open(name, 'rb') as f:
                return self.upload_file_object(f, name, params)
        finally:
            os.remove(name)

    def upload_file_object(self, file_object, name, params=None):
        params = params or {}
        params['api_key'] = self.api_key
        relative_path = '{}/{}'.format(DATASETS_BASE_PATH, name)

        try:
            response = self.auth_client.send(relative_path, 'POST', params=params, data=file_object)
            response.raise_for_status()
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code, reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

        return response

    def import_dataset(self, name):
        params = {'api_key': self.api_key}
        relative_path = '{}/{}/imports'.format(DATASETS_BASE_PATH, name)

        try:
            response = self.auth_client.send(relative_path, 'POST', params=params)
            response.raise_for_status()

            job = response.json()

            return DODatasetJob(job['item_queue_id'], name, self.auth_client)
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code, reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

    def upload_dataframe(self, dataframe, name, params=None):
        params = params or {}
        self.upload(dataframe, name, params)
        job = self.import_dataset(name)
        status = job.result()

        return status

    def download(self, name_id, limit=None, order_by=None):
        params = {
            'api_key': self.api_key
        }

        if limit is not None:
            params['limit'] = limit

        if order_by is not None:
            params['order_by'] = order_by

        relative_path = '{}/{}'.format(DATASETS_BASE_PATH, name_id)

        try:
            response = self.auth_client.send(relative_path, 'GET', params=params, stream=True)
            response.raise_for_status()
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code, reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

        return response

    def download_stream(self, name_id, limit=None, order_by=None):
        return ResponseStream(self.download(name_id, limit=limit, order_by=order_by))

    def create(self, payload):
        params = {'api_key': self.api_key}
        relative_path = DATASETS_BASE_PATH

        try:
            response = self.auth_client.send(relative_path, 'POST', params=params, json=payload)
            response.raise_for_status()
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code, reason)
                raise CartoException(error_msg)
            else:
                raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

        return response

    def enrichment(self, payload):
        params = {'api_key': self.api_key}
        relative_path = ENRICHMENT_BASE_PATH

        try:
            response = self.auth_client.send(relative_path, 'POST', params=params, json=payload)
            response.raise_for_status()

            body = response.json()
            job = DOEnrichmentJob(body['job_id'], self.auth_client)
            status = job.result()

            return status
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code, reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

    def metadata(self, entity, filters):
        params = {'api_key': self.api_key}
        if filters is not None:
            params.update(filters)
        relative_path = os.path.join(METADATA_BASE_PATH, entity)

        try:
            response = self.auth_client.send(relative_path, 'GET', params=params)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code, reason)
                raise CartoException(error_msg)
            else:
                raise CartoException(e)
        except Exception as e:
            raise CartoException(e)


class DODatasetJob:

    def __init__(self, job_id, name_id, auth_client):
        self.id = job_id
        self.name = name_id
        self.auth_client = auth_client
        self.api_key = getattr(self.auth_client, 'api_key', None)

    def status(self):
        params = {'api_key': self.api_key}
        relative_path = '{}/{}/imports/{}'.format(DATASETS_BASE_PATH, self.name, self.id)

        try:
            response = self.auth_client.send(relative_path, 'GET', params=params)
            response.raise_for_status()

            body = response.json()

            if body['status'] == 'failure':
                msg = u'Client Error: %s' % (body['errors'][0])
                raise CartoException(msg)

            return body['status']
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code, reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

    def result(self):
        status = self.status()

        while status not in ('success', 'failure'):
            time.sleep(1)
            status = self.status()

        return status


class DOEnrichmentJob:

    def __init__(self, job_id, auth_client):
        self.id = job_id
        self.auth_client = auth_client
        self.api_key = getattr(self.auth_client, 'api_key', None)

    def status(self):
        params = {'api_key': self.api_key}
        relative_path = '{}/{}/status'.format(ENRICHMENT_BASE_PATH, self.id)

        try:
            response = self.auth_client.send(relative_path, 'GET', params=params)
            response.raise_for_status()

            body = response.json()

            if body['status'] == 'failure':
                msg = u'Client Error: %s' % (body['errors'][0])
                raise CartoException(msg)

            return body['status']
        except requests.HTTPError as e:
            if 400 <= response.status_code < 500:
                # Client error, provide better reason
                reason = response.json()['errors'][0]
                error_msg = u'%s Client Error: %s' % (response.status_code, reason)
                raise CartoException(error_msg)
            raise CartoException(e)
        except Exception as e:
            raise CartoException(e)

    def result(self):
        status = self.status()

        while status not in ('success', 'failure'):
            time.sleep(1)
            status = self.status()

        return status


class DODataset:

    def __init__(self, name=None, columns=None, ttl_seconds=None, client=None, auth_client=None):
        self._name = name
        self._columns = columns or []
        self._ttl_seconds = ttl_seconds
        self._client = client or _DODatasetClient(auth_client)

    @staticmethod
    def _map_type(in_type):
        if in_type in TYPES_MAPPING:
            out_type = TYPES_MAPPING[in_type]
        else:
            out_type = in_type
        return out_type

    def name(self, name):
        self._name = name
        return self

    def column(self, name=None, type=None):
        # TODO validate field names
        type = type.upper()
        if type not in VALID_TYPES:
            # TODO custom exception
            raise Exception('Invalid type %s' % type)
        self._columns.append((name, type))
        return self

    def ttl_seconds(self, ttl_seconds):
        self._ttl_seconds = ttl_seconds
        return self

    def create(self):
        payload = {
            'id': self._name,
            'schema': [{'name': c[0], 'type': self._map_type(c[1])} for c in self._columns],
        }
        if self._ttl_seconds is not None:
            payload['ttl_seconds'] = self._ttl_seconds
        self._client.create(payload)

    def download_stream(self, limit=None, order_by=None):
        return self._client.download_stream(name_id=self._name, limit=limit, order_by=order_by)

    def upload(self, dataframe, geom_column=None):
        return self._client.upload(dataframe, self._name, params={'geom_column': geom_column})

    def upload_file_object(self, file_object, geom_column=None):
        return self._client.upload_file_object(file_object, self._name, params={'geom_column': geom_column})

    def import_dataset(self):
        return self._client.import_dataset(self._name)

    def upload_dataframe(self, dataframe, geom_column=None):
        return self._client.upload_dataframe(dataframe, self._name, params={'geom_column': geom_column})

    def enrichment(self, geom_type='points', variables=None, filters=None, aggregation=None, output_name=None):
        payload = {
            'type': geom_type,
            'input': self._name,
            'variables': variables,
            'filters': filters,
            'aggregation': aggregation,
            'output': output_name
        }

        return self._client.enrichment(payload)

    def metadata(self, entity, filters):
        return self._client.metadata(entity, filters)
