import unittest
import time

from carto import CartoException, APIKeyAuthClient, NoAuthClient, FileImport, URLImport, SQLCLient, FileImportManager, URLImportManager
from secret import API_KEY, USER, EXISTING_TABLE, IMPORT_FILE, IMPORT_URL


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
        check = False
        try:
            no_auth_key = self.client.api_key
        except AttributeError:
            check = True
        self.assertTrue(check)

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
        fi = FileImport(IMPORT_FILE, self.client)
        all_imports = manager.all()
        self.assertEqual(len(all_imports), 1)
        import_id = all_imports[0].id
        self.assertIsNotNone(import_id)

    def test_updated_job_id(self):
        fi = FileImport(IMPORT_FILE, self.client)
        fi.run()
        self.assertEqual(fi.success, True)
        initial_id = fi.id
        has_state = True
        try:
            state = fi.state
        except AttributeError:
            has_state = False
        self.assertEqual(has_state, False)
        fi.update()
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
            time.sleep(5)
            fi.update()
            if count == 10:
                raise Exception("The state is incorrectly stored as: " + fi.state)
        self.assertEqual(fi.state, 'failure')





if __name__ == '__main__':
    unittest.main()
