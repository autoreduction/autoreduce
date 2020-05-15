# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Test the Message class
"""
import unittest
import json

import attr

from message.job import Message


class TestMessage(unittest.TestCase):
    """
    Test cases for the Message class used with AMQ
    """

    @staticmethod
    def _empty():
        """ Create and return an empty message object and corresponding dictionary"""
        empty_msg = Message()
        empty_dict = {'description': None,
                      'facility': None,
                      'run_number': None,
                      'instrument': None,
                      'rb_number': None,
                      'started_by': None,
                      'file_path': None,
                      'overwrite': None,
                      'run_version': None,
                      'job_id': None,
                      'reduction_script': None,
                      'reduction_arguments': None,
                      'reduction_log': None,
                      'admin_log': None,
                      'return_message': None,
                      'retry_in': None}
        return empty_msg, empty_dict

    @staticmethod
    def _populated():
        """ Create and return a populated message object and corresponding dictionary """
        run_number = 11111
        rb_number = 22222
        description = 'test message'
        populated_msg = Message(run_number=run_number,
                                rb_number=rb_number,
                                description=description)
        populated_dict = {'description': description,
                          'facility': None,
                          'run_number': run_number,
                          'instrument': None,
                          'rb_number': rb_number,
                          'started_by': None,
                          'data': None,
                          'overwrite': None,
                          'run_version': None,
                          'job_id': None,
                          'reduction_script': None,
                          'reduction_arguments': None,
                          'reduction_log': None,
                          'admin_log': None,
                          'message': None,
                          'retry_in': None,
                          'reduction_data': None,
                          'run_description': None,
                          'error': None
                          }
        return populated_msg, populated_dict

    def test_init(self):
        """
        Test: All the expected member variables are created
        When: The class is initialised
        """
        empty_msg, _ = self._empty()
        self.assertIsNone(empty_msg.description)
        self.assertIsNone(empty_msg.facility)
        self.assertIsNone(empty_msg.run_number)
        self.assertIsNone(empty_msg.instrument)
        self.assertIsNone(empty_msg.rb_number)
        self.assertIsNone(empty_msg.started_by)
        self.assertIsNone(empty_msg.data)
        self.assertIsNone(empty_msg.overwrite)
        self.assertIsNone(empty_msg.run_version)
        self.assertIsNone(empty_msg.job_id)
        self.assertIsNone(empty_msg.reduction_script)
        self.assertIsNone(empty_msg.reduction_arguments)
        self.assertIsNone(empty_msg.reduction_log)
        self.assertIsNone(empty_msg.admin_log)
        self.assertIsNone(empty_msg.message)
        self.assertIsNone(empty_msg.retry_in)
        self.assertIsNone(empty_msg.reduction_data)
        self.assertIsNone(empty_msg.run_description)
        self.assertIsNone(empty_msg.error)

    def test_to_dict_populated(self):
        """
        Test: A dictionary with populated values in produced
        When: attr.asdict() is called on a Message with populated values
        """
        populated_msg, populated_dict = self._populated()
        actual = attr.asdict(populated_msg)
        self.assertEqual(actual, populated_dict)

    def test_serialize_populated(self):
        """
        Test: An expected JSON object is produced
        When: The Message class is serialised
        """
        populated_msg, populated_dict = self._populated()
        serialized = populated_msg.serialize()
        actual = json.loads(serialized)
        self.assertEqual(actual, populated_dict)

    def test_deserialize_populated(self):
        """
        Test: A Dictionary with all the expected value is produced
        When: A populated serialized object is deserialized
        """
        populated_msg, populated_dict = self._populated()
        serialized = populated_msg.serialize()
        actual = populated_msg.deserialize(serialized)
        self.assertEqual(actual, populated_dict)

    def test_populate_from_dict_overwrite_true(self):
        """
        Test: Values are added and overwritten in the member variables
        When: Message.populate() is called with a non-empty dictionary and overwrite is True
        """
        _, populated_dict = self._populated()
        actual, _ = self._empty()
        actual.populate(source=populated_dict, overwrite=True)
        self.assertEqual(attr.asdict(actual), populated_dict)

    def test_populate_from_dict_overwrite_false(self):
        """
        Test: Values are added but NOT overwritten in the member variables
        When: Message.populate() is called with a non-empty dictionary and overwrite is False
        """
        populated_msg, populated_dict = self._populated()
        populated_dict['job_id'] = 123
        populated_dict['rb_number'] = 33333
        actual, _ = self._populated()
        actual.populate(source=populated_dict, overwrite=False)
        self.assertEqual(actual.rb_number, populated_msg.rb_number)
        self.assertEqual(actual.job_id, 123)

    def test_populate_from_serialized_overwrite_true(self):
        """
        Test: Values are added and overwritten in the member variables
        When: Message.populate() called with a non-empty serialized object and overwrite is True
        """
        populated_msg, populated_dict = self._populated()
        serialized = populated_msg.serialize()
        actual, _ = self._empty()
        actual.populate(source=serialized, overwrite=True)
        self.assertEqual(attr.asdict(actual), populated_dict)

    def test_populate_from_serialized_overwrite_false(self):
        """
        Test: Values are added but NOT overwritten in the member variables
        When: Message.populate() called with a non-empty serialized object and overwrite is False
        """
        new_msg, _ = self._populated()
        new_msg.job_id = 123
        new_msg.rb_number = 33333
        serialized = new_msg.serialize()
        actual, _ = self._populated()
        original, _ = self._populated()
        actual.populate(source=serialized, overwrite=False)
        self.assertEqual(actual.rb_number, original.rb_number)
        self.assertEqual(actual.job_id, 123)

    def test_invalid_serialized(self):
        """
        Test: A ValueError is raised
        When: An invalid serialized object is supplied to Message.populate()
        """
        serialized = 'test'
        empty_msg, _ = self._empty()
        self.assertRaises(ValueError, empty_msg.populate, serialized)
