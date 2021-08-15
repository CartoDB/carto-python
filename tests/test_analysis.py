from carto.analysis import AnalysisClient


def test_analysis(api_key_auth_client_usr, mock_requests):
    analysis = AnalysisClient(api_key_auth_client_usr)
    with mock_requests.mocker:
        jobs = analysis.list_jobs()
        assert len(jobs) > 0

        job_def = {
                "name": "kmeans-test",
                "image": "rafatower/kmeans:v1.0.0",
                "version": "1.0.0",
                "description": "KMeans clusters",
                "parameters": ["n_clusters", "dataset", "columns"]
            }
        result = analysis.create_job(job_def)
        job_id = result.get('job_id')
        assert job_id is not None

        result = analysis.read_job(job_id)
        assert result.get('job_id') == job_id

        job_params = {
            "n_clusters": 3,
            "dataset": "brooklyn_poverty",
            "columns": ["poverty_per_pop"]
        }
        result = analysis.schedule_job(job_id, job_params, on_changed_table='jgoizueta.brooklyn_poverty')
        assert result.get('schedule_id') is not None

        result = analysis.schedule_job(job_id, job_params)
        schedule_id = result.get('schedule_id')
        assert schedule_id is not None

        result = analysis.list_schedules(job_id)
        assert len(result) == 2

        dead = False
        while not dead:
            result = analysis.schedule_status(job_id, schedule_id)
            dead = result['status'] == 'dead'
            result = analysis.schedule_executions(job_id, schedule_id)
            if dead:
                exec_id = result[-1]['execution_id']
                logs = analysis.execution_logs(job_id, schedule_id, exec_id)
                assert len(logs) > 0
                result = analysis.execution_log(job_id, schedule_id, exec_id)

        result = analysis.stop_schedules(job_id)
        assert len(result.get('schedule_ids')) == 2
        result = analysis.remove_job(job_id)
        assert len(result.get('schedule_ids')) == 2
        assert result.get('stopped') == 2
