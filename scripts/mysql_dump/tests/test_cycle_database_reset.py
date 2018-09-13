"""
Test package for DatabaseReset
"""
import unittest

from scripts.mysql_dump.reset_database_post_cycle import DatabaseReset


# pylint:disable=missing-docstring,protected-access
class TestMySQLDump(unittest.TestCase):

    def test_invalid_cycle(self):
        self.assertRaisesRegexp(RuntimeError, 'not_cycle did not match the expected regex',
                                DatabaseReset, 'not_cycle', 'user', 'host', '1234')
        self.assertRaisesRegexp(RuntimeError, 'cycle_100_10 did not match the expected regex',
                                DatabaseReset, 'cycle_100_10', 'user', 'host', '1234')

    def test_invalid_user(self):
        self.assertRaisesRegexp(RuntimeError, '\'User\' for database required',
                                DatabaseReset, 'cycle_10_1', '', 'host', '1234')

    def test_invalid_host(self):
        self.assertRaisesRegexp(RuntimeError, '\'Host\' for database required',
                                DatabaseReset, 'cycle_10_1', 'user', '', '1234')

    def test_invalid_port(self):
        self.assertRaisesRegexp(RuntimeError, '\'Port\' for database required',
                                DatabaseReset, 'cycle_10_1', 'user', 'host', '')
        self.assertRaisesRegexp(RuntimeError, '\'Port\' must be an integer',
                                DatabaseReset, 'cycle_10_1', 'user', 'host', 'string')

    def test_generate_arguments_all(self):
        database_reset = DatabaseReset(latest_cycle='cycle_10_1',
                                       user='user',
                                       password='password',
                                       host='host',
                                       port='1234')
        self.assertEqual(database_reset._generate_argument_string(),
                         '-u user --password=password -h host -P 1234')

    def test_generate_arguments_no_pass(self):
        database_reset = DatabaseReset(latest_cycle='cycle_10_1',
                                       user='user',
                                       host='host',
                                       port='1234')
        self.assertEqual(database_reset._generate_argument_string(),
                         '-u user -h host -P 1234')
