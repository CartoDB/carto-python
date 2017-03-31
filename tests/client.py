import unittest
import time
import requests


from carto import CartoException, APIKeyAuthClient, NoAuthClient, FileImport, URLImport, SQLClient, FileImportManager, ExportJob, NamedMap, NamedMapManager, BatchSQLClient, BatchSQLManager
from secret import API_KEY, USERNAME, EXISTING_POINT_DATASET, EXPORT_VIZ_ID, IMPORT_FILE, IMPORT_URL, NAMED_MAP_AUTH_TOKEN, NAMED_MAP_DEFINITION, NAMED_MAP_INSTANTIATION, BATCH_SQL_SINGLE_QUERY, BATCH_SQL_MULTI_QUERY


class FileImportTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USERNAME)

    def test_file_import(self):
        fi = FileImport(IMPORT_FILE, self.client)
        fi.run()
        self.assertIsNotNone(fi.id)

    def test_url_import(self):
        fi = URLImport(IMPORT_URL, self.client)
        fi.run()
        self.assertIsNotNone(fi.id)

    def test_sync_import(self):
        fi = URLImport(IMPORT_URL, self.client, interval=3600)
        fi.run()
        self.assertIsNotNone(fi.id)

    def test_import_jobs_length(self):
        import_id = None
        manager = FileImportManager(self.client)
        all_imports = manager.all()
        self.assertEqual(len(all_imports), 1)
        import_id = all_imports[0].id
        self.assertIsNotNone(import_id)

    def test_updated_job_id(self):
        fi = FileImport(IMPORT_FILE, self.client)
        fi.run()
        self.assertEqual(fi.success, True)
        initial_id = fi.id
        has_state = True if hasattr(fi, "state") else False
        self.assertEqual(has_state, False)
        fi.update()
        self.assertEqual(hasattr(fi, "state"), True)
        final_id = fi.id
        self.assertEqual(initial_id, final_id)


class ImportErrorTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USERNAME)

    def test_error_handling(self):
        fi = FileImport("test/fake.html", self.client)
        fi.run()
        self.assertEqual(fi.success, True)
        fi.update()
        count = 0
        while fi.state != 'failure':
            if count == 10:
                raise Exception("The state is incorrectly stored as: " + fi.state)
            time.sleep(5)
            fi.update()
            count += 1
        self.assertEqual(fi.state, 'failure')


class CartoExportTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USERNAME)
        self.sql = SQLClient(self.client)

    def test_export_url_exists(self):
        if not EXPORT_VIZ_ID:
            return

        export_job = ExportJob(self.client, EXPORT_VIZ_ID)
        export_job.run()
        count = 0
        while export_job.state != "complete":
            if count == 10:
                raise Exception("The job did not complete in a reasonable time and its state is stored as: " + export_job.state)
            time.sleep(5)
            export_job.update()
            count += 1
        self.assertIsNotNone(export_job.url)


if __name__ == '__main__':
    unittest.main()
