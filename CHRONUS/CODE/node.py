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
    """This class represents a node in the Chord Network"""
    ID = 0
    IPAddr = getHostIP()
    ctrlPort = 7228
    #this seems like a security concern
    predecessor = None
    successor = None
    finger = []

    def __init__(self):
        for i in range(0,KEY_SIZE):
            self.finger.append(None)

    def __eq__(self, other):
        if (self.ID == other.ID and self.IPAddr == other.IPAddr and self.ctrlPort == other.ctrlPort):
            return True
        return False

    # must we modify for asynchronus networking magic?
    def find_successor(self, key):
        if between(key, self.ID, self.successor.ID):
            return self.successor
        else:
            closest = closest_preceding_node(key)
            #closest =  actual node
            return closest.find_successor(key)

    # search the finger table for the highest predessor for key
    def closest_preceding_node(self,key):
        for i in reversed(range(0, KEY_SIZE)):  # or should it be range(KEY_SIZE - 1, -1, -1))
            if self.finger[i] != None: 
                if between(self.finger[i].ID, self.ID, key): #Stoica's paper indexes at 1, not 0
                    return self.finger[i]
        return self

    
    # create a new Chord ring.
    def create(self):
        self.predecessor = None
        self.successor = self

    # join node other's ring
    # this we need to modify for asynchronus stuff 
    def join(self, other):
        self.predecessor = None
    
    def stabalize(self):
        pass
    
    def notify(self,other):
        pass
    
    def fix_fingers(self):
        pass
    
    def check_predecessor(self):
        pass
    
    #returns true if key \in (begin, end]
    #due to nature of the ring, this is not trivial
    #the snipped in the string below is not exactly the same
    """
    ;; reports true if the node is somewhere in the arc of the chord ring spanning nodes x to y, inclusive
    to-report nodeInRange [low high test ]
        let delta (high - low) mod  (2 ^ Hash_Degree) 
    
        report (test - low) mod  (2 ^ Hash_Degree) < delta
    end
    """

    def between(self,key,begin, end):
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
    pass
# Chord Functions
