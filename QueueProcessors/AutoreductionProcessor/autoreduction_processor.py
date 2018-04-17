"""
Module that reads from the reduction pending queue and calls the python script on that data.
"""
import json
import subprocess
import stomp
from twisted.internet import reactor
from autoreduction_logging_setup import logger
from settings import ACTIVEMQ, MISC  # pylint: disable=import-error


class Listener(object):
    """ Listener class that is used to consume messages from ActiveMQ. """
    def __init__(self, client):
        """ Initialise listener. """
        self._client = client
        self.proc_list = []
        self.rb_list = []  # list of RB numbers of active reduction runs
        self.cancel_list = []  # list of (run number, run version)s to drop (once) when we get them

    @staticmethod
    def on_error(message):
        """ Handler for errored messages. """
        logger.error("Error message received - %s", str(message))

    def on_message(self, headers, data):
        """ This method is where consumed messages are dealt with. It will consume a message. """
        destination = headers['destination']
        logger.debug("Received frame destination: %s", destination)
        logger.debug("Received frame priority: %s", headers["priority"])

        self.update_child_process_list()
        data_dict = json.loads(data)

        if "cancel" in data_dict and data_dict["cancel"]:
            self.add_cancel(data_dict)
            return

        self.hold_message(destination, data, headers)

    def hold_message(self, destination, data, headers):
        """ Calls the reduction script. """
        logger.debug("holding thread")
        data_dict = json.loads(data)

        self.update_child_process_list()
        if not self.should_proceed(data_dict):  # wait while the run shouldn't proceed
            reactor.callLater(10, self.hold_message, destination, data, headers)   # pylint: disable=maybe-no-member

            return

        if self.should_cancel(data_dict):
            self.cancel_run(data_dict)  # pylint: disable=maybe-no-member

            return

        print_dict = data_dict.copy()
        print_dict.pop("reduction_script")
        logger.debug("Calling: %s %s %s %s",
                     "python", MISC['post_process_directory'], destination, print_dict)
        self._client.ack(headers['message-id'], headers['subscription'])  # Remove from queue
        proc = subprocess.Popen(["python",
                                 MISC['post_process_directory'],
                                 destination,
                                 data])
        self.add_process(proc, data_dict)

    def update_child_process_list(self):
        """ Updates the list of processes by checking they still exist. """
        for process in self.proc_list:
            if process.poll() is not None:
                index = self.proc_list.index(process)
                self.proc_list.pop(index)
                self.rb_list.pop(index)

    def add_process(self, proc, data_dict):
        """ Add child process to list. """
        self.proc_list.append(proc)
        self.rb_list.append(data_dict["rb_number"])

    def should_proceed(self, data_dict):
        """ Check whether there's a job already running with the same RB. """
        if data_dict["rb_number"] in self.rb_list:
            logger.info("Duplicate RB run #%s, waiting for the first to finish.",
                        data_dict["rb_number"])
            return False
        # else return True
        return True

    @staticmethod
    def run_tuple(data_dict):
        """ return the tuple of (run_number, run version) from a dictionary. """
        run_number = data_dict["run_number"]
        run_version = data_dict["run_version"] if data_dict["run_version"] is not None else 0
        return run_number, run_version

    def add_cancel(self, data_dict):
        """ Add this run to the cancel list, to cancel it next time it comes up. """
        tup = self.run_tuple(data_dict)
        if tup not in self.cancel_list:
            self.cancel_list.append(tup)

    def should_cancel(self, data_dict):
        """ Return whether a run is in the list of runs to be canceled. """
        tup = self.run_tuple(data_dict)
        return tup in self.cancel_list

    def cancel_run(self, data_dict):
        """ Cancel the reduction run. """
        tup = self.run_tuple(data_dict)
        self.cancel_list.remove(tup)


class Consumer(object):
    # pylint: disable=too-few-public-methods
    """ Class used to setup the queue listener. """
    def __init__(self):
        """ Initialise consumer. """
        self.consumer_name = "queueProcessor"

    def run(self):
        """
        Connect to ActiveMQ and listen to the queue for messages.
        """
        brokers = [(ACTIVEMQ['brokers'].split(':')[0], int(ACTIVEMQ['brokers'].split(':')[1]))]
        connection = stomp.Connection(host_and_ports=brokers, use_ssl=False)
        connection.set_listener(self.consumer_name, Listener(connection))
        logger.info("Starting ActiveMQ Connection to %s", ACTIVEMQ['brokers'])
        connection.start()
        logger.info("Completed ActiveMQ Connection")
        connection.connect(ACTIVEMQ['amq_user'],
                           ACTIVEMQ['amq_pwd'],
                           wait=False,
                           header={'activemq.prefetchSize': '1'})

        for queue in ACTIVEMQ['amq_queues']:
            connection.subscribe(destination=queue,
                                 id='1',
                                 ack='client-individual',
                                 header={'activemq.prefetchSize': '1'})
            logger.info("[%s] Subscribing to %s", self.consumer_name, queue)
        logger.info("Successfully subscribed to all of the queues")


def main():
    """ Main method, starts consumer. """
    logger.info("Start post process asynchronous listener!")
    reactor.callWhenRunning(Consumer().run) # pylint: disable=maybe-no-member
    reactor.run() # pylint: disable=maybe-no-member
    logger.info("Stop post process asynchronous listener!")

if __name__ == '__main__':
    main()
