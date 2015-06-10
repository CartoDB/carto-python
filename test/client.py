import unittest
from cartodb import CartoDBOAuth as CartoDB, CartoDBException, CartoDBAPIKey, FileImport, URLImport

from secret import *


class CartoDBClientTest(object):
    def test_sql_error(self):
        self.assertRaises(CartoDBException, self.client.sql, 'select * from non_existing_table')

    def test_sql_error_get(self):
        self.assertRaises(CartoDBException, self.client.sql, 'select * from non_existing_table', {'do_post': False})

    def test_sql(self, do_post=True):
        data = self.client.sql('select * from ' + EXISTING_TABLE, do_post=do_post)
        self.assertIsNotNone(data)
        self.assertIn('rows', data)
        self.assertIn('total_rows', data)
        self.assertIn('time', data)
        self.assertTrue(len(data['rows']) > 0)

    def test_sql_get(self):
        self.test_sql(do_post=False)


class CartoDBClientTestOAuth(CartoDBClientTest, unittest.TestCase):
    def setUp(self):
        self.client = CartoDB(CONSUMER_KEY, CONSUMER_SECRET, user, password, user)


class CartoDBClientTestApiKey(CartoDBClientTest, unittest.TestCase):
    def setUp(self):
        self.client = CartoDBAPIKey(API_KEY, user)


class CartoDBClientTestApiKeyV2(CartoDBClientTest, unittest.TestCase):
    def setUp(self):
        self.client = CartoDBAPIKey(API_KEY, user, api_version='v2')


class CartoDBClientTestImportAPI(unittest.TestCase):
    def setUp(self):
        self.client = CartoDBAPIKey(API_KEY, user)

    def test_file_import(self):
        fi = FileImport(IMPORT_FILE, self.client)
        fi.run()
        self.assertIsNotNone(fi.id)

    def test_url_import(self):
        fi = URLImport(IMPORT_URL, self.client)
        fi.run()
        self.assertIsNotNone(fi.id)


if __name__ == '__main__':
    unittest.main()

