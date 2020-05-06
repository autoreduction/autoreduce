# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Represents the messages passed between AMQ queues
"""
import json
import attr


# pylint:disable=too-many-instance-attributes
@attr.s
class Message:
    """
    A class that represents an AMQ Message.
    Messages can be serialized and deserialized for sending messages to and from AMQ
    """
    description = attr.ib(default=None)
    facility = attr.ib(default=None)
    run_number = attr.ib(default=None)
    instrument = attr.ib(default=None)
    rb_number = attr.ib(default=None)
    started_by = attr.ib(default=None)
    file_path = attr.ib(default=None)
    overwrite = attr.ib(default=None)
    run_version = attr.ib(default=None)
    job_id = attr.ib(default=None)
    reduction_script = attr.ib(default=None)
    reduction_arguments = attr.ib(default=None)
    reduction_log = attr.ib(default=None)
    admin_log = attr.ib(default=None)
    return_message = attr.ib(default=None)
    retry_in = attr.ib(default=None)

    # Note: since most uses of a message will immediately require populate() after initialisation,
    #   adding population_source as an init arg cuts down a step
    #   i.e. Message().populate(DICT) --> Message(DICT)     [but the former method will still work]
    def init(self, population_source=None):
        if population_source:
            self.populate(population_source)

    def serialize(self):
        """
        Serialized member variables as a json dump
        :return: JSON dump of a dictionary representing the member variables
        """
        return json.dumps(attr.asdict(self))

    @staticmethod
    def deserialize(serialized_object):
        """
        Deserialize an object and return a dictionary of that object
        :param serialized_object: The object to deserialize
        :return: Dictionary of deserialized object
        """
        return json.loads(serialized_object)

    def populate(self, source, overwrite=True):
        """
        Populate the class from either a serialised object or a dictionary optionally retaining
        or overwriting existing values of attributes
        :param source: Object to populate class from
        :param overwrite: If True, overwrite existing values of attributes
        """
        if isinstance(source, str):
            try:
                source = self.deserialize(source)
            except json.decoder.JSONDecodeError:
                raise ValueError(f"Unable to recognise serialized object {source}")

        self_dict = attr.asdict(self)
        for key, value in source.items():
            if key in self_dict.keys():
                self_value = self_dict[key]
                if overwrite or self_value is None:
                    # Set the value of the variable on this object accessing it by name
                    setattr(self, key, value)
