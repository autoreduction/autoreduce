## QueueProcessors *(linux only)*

Scripts that perform the main flow control in the system by ingesting and sending messages from the messenging server, ActiveMQ.
This handles the ActiveMQ queues and is the section of the code that deals with reduction.

Service components of Autoreduction can in general be setup on more than one OS (platform). However, the QueueProcesor must be run on linux based systems due to it's implementation of Daemons. We have so far not be presented with a need to run this service component on another platform.

To start the QueueProcessors run:
```
$ ./restart.sh
```
