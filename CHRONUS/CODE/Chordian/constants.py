
#constants

SERVICE_SHELVER = "SERVICE_SHELVER"
SERVICE_NETWORK = "SERVICE_NETWORK"
SERVICE_INTERNAL = "SERVICE_INTERNAL"
SERVICE_NODE = "SERVICE_NODE"
SERVICE_ECHO = "SERVICE_ECHO"
SERVICE_DATABASE = "SERVICE_DATABASE"
SERVICE_TOPOLOGY = "SERVICE_TOPOLOGY"
SERVICE_FILE = "SERVICE_FILE"


NETWORK_TERMINATE = "NETWORK_TERMINATE"
NETWORK_PEER_CONNECT = "NETWORK_PEER_CONNECT"
NETWORK_PEER_DISCONNECT = "NETWORK_PEER_DISCONNECT"
NETWORK_PEER_CONNECTED = "NETWORK_PEER_CONNECTED"
NETWORK_PEER_DISCONNECTED = "PEER_DISCONNECTED"
NETWORK_PEER_DATA_SENT = "NETWORK_PEER_DATA_SENT"
NETWORK_PEER_DATA_RECEIVED = "NETWORK_PEER_DATA_RECEIVED"



MESSAGE_START_SERVER = "START_SERVER"
MESSAGE_STOP_SERVER = "STOP_SERVER"
MESSAGE_SEND_PEER_DATA = "SEND_PEER_DATA"
MESSAGE_DISCONNECT_PEER = "DISCONNECT_PEER"

MESSAGE_CONSOLE_COMMAND = "CONSOLE_COMMAND"
MESSAGE_SETUP_NODE = "SETUP_NODE"


MESSAGE_START_SERVER_SUCCEEDED = "START_SERVER_SUCCEEDED"
MESSAGE_START_SERVER_FAILED = "START_SERVER_FAILED"

import time
import os
import sys

class Stopwatch():
    def __init__(self):
        self.t1 = self.t2 = time.time( )

    def start(self):
        self.t1 = time.time()

    def reset(self):
        self.t1 = self.t2 = time.time()

    def stop(self):
        self.t2 = time.time()

    def elapsed(self, label):
        if self.t2 <= self.t1:
            self.t2 = time.time()
        string = '| %s in %0.3f ms |' % (label, (self.t2-self.t1)*1000.0)
        print '-'*len(string)
        print string
        print '-'*len(string)


    def ms(self):
        t2 = self.t2
        if t2 == self.t1:
            t2 = time.time()
        return (t2-self.t1)*1000.0

def show_error():
    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        msg = ""
        try:
            msg = exc_obj.message if len(exc_obj.message) else exc_obj.strerror
        except:
            pass

        print(exc_type, msg, fname, exc_tb.tb_lineno)
    except:
        raise