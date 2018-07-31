#! /usr/bin/env python
"""
Check the length of the queues
"""
# pylint: disable=duplicate-code
from __future__ import print_function
import sys

import requests
from requests.auth import HTTPBasicAuth

# pylint: disable=import-error
from scripts.NagiosChecks.autoreduce_settings import ACTIVEMQ


ACTIVEMQ_URL = "http://" + ACTIVEMQ['host'] + ACTIVEMQ['api-path']
ACTIVEMQ_AUTH = HTTPBasicAuth(ACTIVEMQ['username'], ACTIVEMQ['password'])


# pylint: disable=invalid-name
def checkQueueLength(warning, critical):
    """
    Ensures that the queue length is as expected
    :param warning: value to start reporting system warning
    :param critical: value to start reporting system critical
    :return: 0 - Success
             1 - Warning
             2 - Critical
    """
    for queue in ACTIVEMQ['queues']:
        r = requests.get(ACTIVEMQ_URL + ",destinationName=" + queue + "/QueueSize",
                         auth=ACTIVEMQ_AUTH)

        queue_length = r.json()['value']
        # print(queue + " length = " + str(queue_length))

        if queue_length > warning:
            print(queue + " queue getting big " + str(queue_length))
            return 1
        if queue_length > critical:
            print(queue + " queue length is critical " + str(queue_length))
            return 2
    return 0


# pylint: disable=using-constant-test
if "__name__":
    sys.exit(checkQueueLength(3, 10))
