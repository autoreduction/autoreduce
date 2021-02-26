# ############################################################################
# Autoreduction Repository :
# https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################
"""
This module deals with the updating of the database backend.
It consumes messages from the queues and then updates the reduction run
status in the database.
"""
import logging
import time
import traceback
from contextlib import contextmanager
from typing import Tuple

from model.message.message import Message
from queue_processors.queue_processor.handle_message import HandleMessage
from utils.clients.queue_client import QueueClient


class QueueListener:
    """ Listener class that is used to consume messages from ActiveMQ. """
    def __init__(self, client: QueueClient):
        """ Initialise listener. """
        self.client: QueueClient = client
        self.message_handler = HandleMessage(queue_listener=self)

        self.logger = logging.getLogger("queue_listener")

        # Keeps track of whether there is currently a message being processed.
        # Just a raw bool is OK because the subscription is configured to
        # prefetch 1 message at a time - i.e. this function should NOT run in parallel
        self._processing = False

    def is_processing_message(self):
        """
        Getter for the processing state
        """
        return self._processing

    @contextmanager
    def mark_processing(self):
        """
        Function usable by using `with ...` for context management
        and to ensure processing is always set to false at the end
        """
        self._processing = True
        try:
            yield
        finally:
            self._processing = False

    def on_message(self, headers, message):
        """ This method is where consumed messages are dealt with. It will
        consume a message. """
        with self.mark_processing():
            destination = headers["destination"]
            priority = headers["priority"]
            self.logger.info("Destination: %s Priority: %s", destination, priority)
            # Load the JSON message and header into dictionaries
            try:
                if not isinstance(message, Message):
                    json_string = message
                    message = Message()
                    message.populate(json_string)
            except ValueError:
                self.logger.error("Could not decode message from %s\n\n%s", destination, traceback.format_exc())
                return

            # the connection is configured with client-individual, meaning that each client
            # has to submit an acknowledgement for receiving the message
            # (otherwise I think that it is not removed from the queue but I am not sure about that)
            self.client.ack(headers["message-id"], headers["subscription"])
            try:
                if destination == '/queue/DataReady':
                    self.message_handler.data_ready(message)
                else:
                    self.logger.error("Received a message on an unknown topic '%s'", destination)
            except Exception as exp:  # pylint:disable=broad-except
                self.logger.error("Unhandled exception encountered: %s %s\n\n%s",
                                  type(exp).__name__, exp, traceback.format_exc())


def setup_connection(consumer_name) -> Tuple[QueueClient, QueueListener]:
    """
    Starts the ActiveMQ connection and registers the event listener
    :return: A client connected and subscribed to the queue specified in credentials, and
             a listener instance which will handle incoming messages
    """
    # Connect to ActiveMQ
    activemq_client = QueueClient()
    activemq_client.connect()

    # Register the event listener
    listener = QueueListener(activemq_client)

    # Subscribe to queues
    activemq_client.subscribe_autoreduce(consumer_name, listener)
    return activemq_client, listener


def main():
    """
    Main method.
    :return: (Listener) returns a handle to a connected Active MQ listener
    """
    return setup_connection('queue_processor')


if __name__ == '__main__':
    try:
        main()

        # print a success message to the terminal in case it's not being run through the daemon
        print("QueueClient connected and QueueListener active.")

        # if running this script as main (e.g. when debigging the queue listener)
        # the activemq connection runs async and without this sleep the process will
        # just connect to activemq then exit completely
        while True:
            time.sleep(0.5)
    except Exception as exp:
        print("This is an exception that needs to be logged")

