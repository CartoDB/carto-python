import unittest
import time


from carto import CartoException, APIKeyAuthClient, NoAuthClient, FileImport, URLImport, SQLCLient, BatchSQLClient, BatchSQLManager, FileImportManager, URLImportManager, ExportJob
from secret import API_KEY, USER, EXISTING_TABLE, IMPORT_FILE, IMPORT_URL, VIZ_EXPORT_ID

class SQLClientTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USER)
        self.sql = SQLCLient(self.client)

    def test_sql_error(self):
        self.assertRaises(CartoException, self.sql.send, 'select * from non_existing_table')

    def test_sql_error_get(self):
        self.assertRaises(CartoException, self.sql.send, 'select * from non_existing_table', {'do_post': False})

    def test_sql(self, do_post=True):
        data = self.sql.send('select * from ' + EXISTING_TABLE, do_post=do_post)
        self.assertIsNotNone(data)
        self.assertIn('rows', data)
        self.assertIn('total_rows', data)
        self.assertIn('time', data)
        self.assertTrue(len(data['rows']) > 0)

    def test_sql_get(self):
        self.test_sql(do_post=False)


class NoAuthClientTest(unittest.TestCase):
    def setUp(self):
        self.client = NoAuthClient(USER)
        self.sql = SQLCLient(self.client)

    def test_no_api_key(self):
        self.assertFalse(hasattr(self.client, "api_key"))

    def test_sql_error(self):
        self.assertRaises(CartoException, self.sql.send, 'select * from non_existing_table')

    def test_sql_error_get(self):
        self.assertRaises(CartoException, self.sql.send, 'select * from non_existing_table', {'do_post': False})

    def test_sql(self, do_post=True):
        data = self.sql.send('select * from ' + EXISTING_TABLE, do_post=do_post)
        self.assertIsNotNone(data)
        self.assertIn('rows', data)
        self.assertIn('total_rows', data)
        self.assertIn('time', data)
        self.assertTrue(len(data['rows']) > 0)

    def test_sql_get(self):
        self.test_sql(do_post=False)


class FileImportTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USER)

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
        time.sleep(5)
        self.assertEqual(fi.state, 'pending')
        final_id = fi.id
        self.assertEqual(initial_id, final_id)


class ImportErrorTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USER)

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
        self.client = APIKeyAuthClient(API_KEY, USER)
        self.sql = SQLCLient(self.client)

    def test_export_url_exists(self):
        export_job = ExportJob(self.client, VIZ_EXPORT_ID, API_KEY)
        export_job.run()
        count = 0
        while (export_job.state != "complete"):
            if count == 10:
                raise Exception("The job did not complete in a reasonable time and its state is stored as: " + export_job.state)
            time.sleep(5)
            export_job.update()
            count += 1
        self.assertIsNotNone(export_job.url)

class BatchSQLTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USER)
        self.sql = BatchSQLClient(self.client)
        self.manager = BatchSQLManager(self.client)
    
    def test_batch_create(self):
        query2 = "update all_day set depth = 100"
        data2 = self.sql.create(query2)
        query = "update qnmappluto set lot = 2022"
        data = self.sql.create(query)
        job_id = data['job_id']
        self.sql.update(job_id, "update qnmappluto set lot = 2112312")
        self.sql.read(job_id)
        confirmation = self.sql.cancel(job_id)
        self.assertEqual(confirmation, 'cancelled')

        all_sql_updates = self.manager.all()
    
    def test_batch_no_auth_error(self):
        switch = False
        no_auth_client = NoAuthClient(USER)
        no_auth_sql = BatchSQLClient(no_auth_client)
        query = "update qnmappluto set lot = 100"
        try:
            data = no_auth_sql.create(query)
        except CartoException:
            switch = True
        self.assertEqual(switch, True)

    def test_batch_multi_sql(self):
        query = [
            "update twitter_breakfast_lunch_dinner set body = 'hi'",
            "update twitter_breakfast_lunch_dinner set twitter_lang = francais",
            "update twitter_breakfast_lunch_dinner set category_name = 123",
            "update twitter_breakfast_lunch_dinner set favoritescount = 10"
        ]
        data = self.sql.create(query)
        job_id = data['job_id']
        confirmation = self.sql.cancel(job_id)
        self.assertEqual(confirmation, 'cancelled')



if __name__ == '__main__':
    unittest.main()
