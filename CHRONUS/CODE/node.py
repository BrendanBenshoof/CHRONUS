#pulled from Benjamin Evans's implementation "pyChordDHT"
### TODO ###
# Finish stabilization
# hash math - some indexes are wrong <- I think this is fixed
# if request times out - use backup node
# update request on node failure
# Not closing connection properly - why?
############


#imports 
from hash_util import *
from socket import *
import time
from threading import *
import signal
import sys
import uuid
import copy
from optparse import OptionParser
import random
import net_server 


# Debug variables
TEST_MODE = True
VERBOSE = True


# Class
class Node():
    """This class is primarily for holding info on 
    other nodes in the network"""
    ID = 0
    IPAddr = getHostIP()
    ctrlPort = 7228

    def __eq__(self, other):
        if (self.ID == other.ID and self.IPAddr == other.IPAddr and self.ctrlPort
            == other.ctrlPort):

            return True
        return False

    def find_successor(self, key):
        pass

    def closest_preceding_node(self,key):
        pass
    
    # create a new Chord ring.
    def create(self):
        pass
    
    def join(self, other):
        pass
    
    def stabalize(self):
        pass
    
    def notify(self,other):
        pass
    
    def fix_fingers(self):
        pass
    
    def check_predecessor(self):
        pass
    
    def update_finger_table(self):
        pass

   

####################### Globals #######################

#Node
thisNode = Node()
thisNode.ID = hash_str(str(uuid.uuid4()) + str(uuid.uuid4()))
thisNode.IPAddr = getHostIP()
thisNode.ctrlPort = 7228

prevNode = thisNode

#Finger table
fingerTable = []
fingerTableLock = Lock()
prevNodeLock = Lock()
numFingerErrors = 0

successorList = []
sucListLock = Lock()
successorOfflineAttempts = 0

#services
services =  {}


#Network connections
servCtrl = None
servRelay = None





# Functions
def add_service(service, callback):
    services[service.attach(callback)] = service
    if VERBOSE: 
        print "Service " + service.service_id + "attached" 

def send_message(msg, destination):
    net_server.send_message(msg.serialize(), destination)

# called when node is passed a message
def handle_message(msg, origin):
    

-
# Chord Functions
