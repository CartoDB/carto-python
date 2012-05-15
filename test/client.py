from cartodb import CartoDBOAuth as CartoDB, CartoDBException, CartoDBAPIKey

import httplib2
import oauth2 as oauth

import unittest

from secret import *

class CartoDBClientTest(object):

    def test_sql_error(self):
        self.assertRaises(CartoDBException, self.client.sql, 'select * from non_existing_table')

    def test_sql_error_get(self):
        self.assertRaises(CartoDBException, self.client.sql, 'select * from non_existing_table', { 'do_post':False})

    def test_sql(self, do_post=True):
        data = self.client.sql('select * from tracker', do_post=do_post)
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


if __name__ == '__main__':
    unittest.main()

