#simpler networking solution
import socket
import threading
import socket
import node
import message
from Queue import *
import time

CHUNKSIZE = 64

import instrumentation as inst

from xmlrpclib import ServerProxy, Error
from SimpleXMLRPCServer import SimpleXMLRPCServer
import time


def recive(data):
    msg = message.Message.deserialize(data)
    inst.addBytes("IN",len(data))
    t = threading.Thread(target=lambda:node.handle_message(msg))
    t.daemon = True
    t.start()    
    return "ACK"



class NETWORK_SERVICE(object):

    def __init__(self,HOST="localhost",PORT=9000):
        # Create the server, binding to localhost on port 9999
        self.server = SimpleXMLRPCServer((HOST, PORT),logRequests=False)
        self.running = True
        self.server.register_function(recive)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C




    def send_message(self,msg,dest):
        time.sleep(0.01)
        data = msg.serialize()
        inst.addBytes("OUT",len(data))
        try:
            server = ServerProxy("http://"+str(dest.IPAddr)+":"+str(dest.ctrlPort))
            server.recive(data)
        except Exception:
            node.message_failed(msg,dest)




