# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
#!/usr/bin/env python
"""
Module for daemonising the queue processor.
"""
import sys
from QueueProcessors.QueueProcessor.daemon import Daemon
from QueueProcessors.QueueProcessor import queue_processor


# pylint:disable=no-self-use,too-few-public-methods
class QueueProcessorDaemon(Daemon):
    """ Queue processor daemoniser """
    def run(self):
        """ Run queue processor. """
        queue_processor.main()
        while True:
            pass


def main():
    """ Main method. """
    daemon = QueueProcessorDaemon('/tmp/QueueProcessorDaemon.pid')
    if len(sys.argv) == 2:
        if sys.argv[1] == 'start':
            daemon.start()
        elif sys.argv[1] == 'stop':
            daemon.stop()
        elif sys.argv[1] == 'restart':
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)


if __name__ == "__main__":
    main()
