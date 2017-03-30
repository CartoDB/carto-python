import unittest
import time
import requests


from carto import CartoException, APIKeyAuthClient, NoAuthClient, FileImport, URLImport, SQLClient, FileImportManager, ExportJob, NamedMap, NamedMapManager, BatchSQLClient, BatchSQLManager
from secret import API_KEY, USERNAME, EXISTING_POINT_DATASET, EXPORT_VIZ_ID, IMPORT_FILE, IMPORT_URL, NAMED_MAP_AUTH_TOKEN, NAMED_MAP_DEFINITION, NAMED_MAP_INSTANTIATION, BATCH_SQL_SINGLE_QUERY, BATCH_SQL_MULTI_QUERY


class APIKeyAuthClientTest(unittest.TestCase):
    def test_cloud_personal_url(self):
        user1 = APIKeyAuthClient('https://user1.carto.com/a/b/c', API_KEY).username
        user2 = APIKeyAuthClient('https://www.user2.carto.com', API_KEY).username
        user3 = APIKeyAuthClient('http://www.user3.carto.com/a/b/c', API_KEY).username
        self.assertEqual(user1, 'user1')
        self.assertEqual(user2, 'user2')
        self.assertEqual(user3, 'user3')

    def test_cloud_organization_url(self):
        user1 = APIKeyAuthClient('https://carto.com/u/user1/a/b/c', API_KEY).username
        user2 = APIKeyAuthClient('https://www.carto.com/u/user2', API_KEY).username
        user3 = APIKeyAuthClient('http://www.carto.com/u/user3/a/b/c', API_KEY).username
        self.assertEqual(user1, 'user1')
        self.assertEqual(user2, 'user2')
        self.assertEqual(user3, 'user3')

    def test_on_prem_url(self):
        user1 = APIKeyAuthClient('https://carto.com/user/user1/a/b/c', API_KEY).username
        user2 = APIKeyAuthClient('https://www.carto.com/user/user2', API_KEY).username
        user3 = APIKeyAuthClient('http://www.carto.com/user/user3/a/b/c', API_KEY).username
        self.assertEqual(user1, 'user1')
        self.assertEqual(user2, 'user2')
        self.assertEqual(user3, 'user3')

class SQLClientTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USERNAME)
        self.sql = SQLClient(self.client)

    def test_sql_error(self):
        self.assertRaises(CartoException, self.sql.send, 'select * from non_existing_dataset')

    def test_sql_error_get(self):
        self.assertRaises(CartoException, self.sql.send, 'select * from non_existing_dataset', {'do_post': False})

    def test_sql(self, do_post=True):
        data = self.sql.send('select * from ' + EXISTING_POINT_DATASET, do_post=do_post)
        self.assertIsNotNone(data)
        self.assertIn('rows', data)
        self.assertIn('total_rows', data)
        self.assertIn('time', data)
        self.assertTrue(len(data['rows']) > 0)

    def test_sql_get(self):
        self.test_sql(do_post=False)


class NoAuthClientTest(unittest.TestCase):
    def setUp(self):
        self.client = NoAuthClient(USERNAME)
        self.sql = SQLClient(self.client)

    def test_no_api_key(self):
        self.assertFalse(hasattr(self.client, "api_key"))

    def test_sql_error(self):
        self.assertRaises(CartoException, self.sql.send, 'select * from non_existing_dataset')

    def test_sql_error_get(self):
        self.assertRaises(CartoException, self.sql.send, 'select * from non_existing_dataset', {'do_post': False})


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


class NamedMapTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USERNAME)

    def test_named_map_methods(self):
        # Create named map
        named = NamedMap(self.client, params=NAMED_MAP_DEFINITION)
        named.save()
        self.assertIsNotNone(named.template_id)

        # Instantiate named map
        named.instantiate(NAMED_MAP_INSTANTIATION, NAMED_MAP_AUTH_TOKEN)
        self.assertIsNotNone(named.layergroupid)

        # Update named map
        del named.view
        named.save()
        self.assertFalse(hasattr(named, 'view'))

        # Delete named map
        self.assertEqual(named.delete(), requests.codes.no_content)

    def test_named_map_manager(self):
        named_manager = NamedMapManager(self.client)

        # Get all named maps
        initial_maps = named_manager.all(ids_only=False)

        # Create named map
        named = NamedMap(self.client, params=NAMED_MAP_DEFINITION)
        named.save()
        self.assertIsNotNone(named.template_id)

        # Get all named maps again
        final_maps = named_manager.all(ids_only=False)

        # Check number of maps is correct
        self.assertEqual(len(initial_maps) + 1, len(final_maps))

        # Delete named map simply to avoid polluting the user's account
        self.assertEqual(named.delete(), requests.codes.no_content)


class BatchSQLTest(unittest.TestCase):
    def setUp(self):
        self.client = APIKeyAuthClient(API_KEY, USERNAME)
        self.sql = BatchSQLClient(self.client)
        self.manager = BatchSQLManager(self.client)

    def test_batch_create(self):
        # Create query
        data = self.sql.create(BATCH_SQL_SINGLE_QUERY)

        # Update status
        job_id = data['job_id']

        # Cancel if not finished
        try:
            confirmation = self.sql.cancel(job_id)
        except CartoException:
            pass
        else:
            self.assertEqual(confirmation, 'cancelled')

        # Get all
        all_sql_updates = self.manager.all()
        self.assertIsNotNone(all_sql_updates)

    def test_batch_no_auth_error(self):
        no_auth_client = NoAuthClient(USERNAME)
        try:
            no_auth_sql = BatchSQLClient(no_auth_client)
        except CartoException:
            no_auth_sql = None
        self.assertIsNone(no_auth_sql)

    def test_batch_multi_sql(self):
        # Create query
        data = self.sql.create(BATCH_SQL_MULTI_QUERY)

        # Update status
        job_id = data['job_id']

        # Cancel if not finished
        try:
            confirmation = self.sql.cancel(job_id)
        except CartoException:
            pass
        else:
            self.assertEqual(confirmation, 'cancelled')


if __name__ == '__main__':
    unittest.main()
