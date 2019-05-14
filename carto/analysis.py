SQL_API_URL = 'api/{api_version}/analysis'

HEADERS = {
    'content-type': 'application/json',
    'accept': 'application/json'
}

class AnalysisClient(object):
    def __init__(self, auth_client, api_version='v4'):
        self.auth_client = auth_client
        self.api_url = SQL_API_URL.format(api_version=api_version)

        self.api_key = getattr(self.auth_client, 'api_key', None)
        self.username = getattr(self.auth_client, 'username', None)
        self.base_url = self.auth_client.base_url

    def _url(self, *parts):
        return '/'.join((self.api_url,) + parts)

    def list_jobs(self):
        res = self.auth_client.send(self._url('jobs'), 'GET', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def create_job(self, job_definition):
        url = self._url('jobs')
        res = self.auth_client.send(url, 'POST', json=job_definition, headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def read_job(self, job_id):
        url = self._url('jobs', job_id)
        res = self.auth_client.send(url, 'GET', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def schedule_job(
        self, job_id, job_params, schedule=None, on_changed_table=None
    ):
        url = self._url('jobs', job_id, 'schedule')
        params = {}
        if schedule:
            params['schedule'] = schedule
        if on_changed_table:
            params['on_changed_table'] = on_changed_table
        res = self.auth_client.send(url, 'POST', params=params, json=job_params, headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def list_schedules(self, job_id):
        url = self._url('jobs', job_id, 'schedules')
        res = self.auth_client.send(url, 'GET', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def schedule_status(self, job_id, schedule_id):
        url = self._url('jobs', job_id, 'schedule', schedule_id)
        res = self.auth_client.send(url, 'GET', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def schedule_executions(self, job_id, schedule_id):
        url = self._url('jobs', job_id, 'schedule', schedule_id, 'executions')
        res = self.auth_client.send(url, 'GET', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def execution_log(
        self, job_id, schedule_id, execution_id, type='stdout', offset=None
    ):
        url = self._url(
            'jobs', job_id,
            'schedule', schedule_id,
            'execution', execution_id,
            'log'
        )
        res = self.auth_client.send(url, 'GET', params={'type': type, 'offset': offset}, headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def execution_logs(self, job_id, schedule_id, execution_id):
        url = self._url(
            'jobs', job_id,
            'schedule', schedule_id,
            'execution', execution_id,
            'debug'
        )
        res = self.auth_client.send(url, 'GET', headers=HEADERS)
        return self.auth_client.get_response_data(res, False)

    def remove_job(self, job_id):
        url = self._url('jobs', job_id)
        res = self.auth_client.send(url, 'DELETE', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def stop_schedule(self, job_id, schedule_id):
        url = self._url('jobs', job_id, 'schedule', schedule_id)
        res = self.auth_client.send(url, 'DELETE', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def stop_schedules(self, job_id):
        url = self._url('jobs', job_id, 'schedules')
        res = self.auth_client.send(url, 'DELETE', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)
