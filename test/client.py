import unittest
import time
import json


from carto import CartoException, APIKeyAuthClient, NoAuthClient, FileImport, URLImport, SQLClient, FileImportManager, URLImportManager, ExportJob, NamedMap, NamedMapManager, BatchSQLClient, BatchSQLManager
from secret import API_KEY, USER, EXISTING_TABLE, IMPORT_FILE, IMPORT_URL, VIZ_EXPORT_ID, NAMED_MAP_TEMPLATE1, TEMPLATE1_NAME, TEMPLATE1_AUTH_TOKEN, NAMED_MAP_TEMPLATE2, NAMED_MAP_PARAMS, BATCH_SQL_SINGLE_QUERY, BATCH_SQL_MULTI_QUERY


class SQLClientTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USER)
        self.sql = SQLClient(self.client)

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
        self.sql = SQLClient(self.client)

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
        self.assertEqual(hasattr(fi, "state"), True)
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
        self.sql = SQLClient(self.client)

    def test_export_url_exists(self):
        export_job = ExportJob(self.client, VIZ_EXPORT_ID)
        export_job.run()
        count = 0
        while (export_job.state != "complete"):
            if count == 10:
                raise Exception("The job did not complete in a reasonable time and its state is stored as: " + export_job.state)
            time.sleep(5)
            export_job.update()
            count += 1
        self.assertIsNotNone(export_job.url)


class NamedMapTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USER)

    def test_named_map_methods(self):
        temp_file = open(NAMED_MAP_TEMPLATE1)
        named = NamedMap(self.client, params=json.load(temp_file))
        named.save()
        self.assertIsNotNone(named.template_id)
        temp_id = named.template_id
        param_file = open(NAMED_MAP_PARAMS)
        named.instantiate(json.load(param_file), TEMPLATE1_AUTH_TOKEN)
        self.assertIsNotNone(named.layergroupid)
        del named.view
        named.save()
        self.assertEqual(False, hasattr(named, 'view'))
        check_deleted = named.delete()
        self.assertEqual(check_deleted, 204)

    def test_named_map_manager(self):
        temp_file = open(NAMED_MAP_TEMPLATE1)
        named = NamedMap(self.client, params=json.load(temp_file))
        named_manager = NamedMapManager(self.client)
        initial_maps = named_manager.all(ids_only=False)
        named.save()
        param_file = open(NAMED_MAP_PARAMS)
        named.instantiate(json.load(param_file), TEMPLATE1_AUTH_TOKEN)
        temp_id = named.template_id
        test = named_manager.get(id=TEMPLATE1_NAME)
        temp_file2 = open(NAMED_MAP_TEMPLATE2)
        named2 = NamedMap(self.client, params=json.load(temp_file2))
        named2.save()
        all_maps = named_manager.all(ids_only=False)
        self.assertEqual(len(initial_maps) + 2, len(all_maps))
        check_deleted = named.delete()
        self.assertEqual(check_deleted, 204)
        check_deleted2 = named2.delete()
        self.assertEqual(check_deleted2, 204)


class BatchSQLTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USER)
        self.sql = BatchSQLClient(self.client)
        self.manager = BatchSQLManager(self.client)
    
    def test_batch_create(self):
        query = BATCH_SQL_SINGLE_QUERY
        data = self.sql.create(query)
        job_id = data['job_id']
        read = self.sql.read(job_id)
        confirmation = self.sql.cancel(job_id)
        self.assertEqual(confirmation, 'cancelled')
        all_sql_updates = self.manager.all()
        self.assertIsNotNone(all_sql_updates)
    
    def test_batch_no_auth_error(self):
        switch = False
        no_auth_client = NoAuthClient(USER)
        try:
            no_auth_sql = BatchSQLClient(no_auth_client)
        except CartoException:
            switch = True
        self.assertEqual(switch, True)

    def test_batch_multi_sql(self):
        query = BATCH_SQL_MULTI_QUERY
        data = self.sql.create(query)
        job_id = data['job_id']
        confirmation = self.sql.cancel(job_id)
        self.assertEqual(confirmation, 'cancelled')


if __name__ == '__main__':
    unittest.main()
