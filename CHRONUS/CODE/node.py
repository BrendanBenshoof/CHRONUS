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
import dummy_network as net_server 


# Debug variables
TEST_MODE = False
VERBOSE = True

class Node_Info():
    #this is a struct to hold info on other nodes
    def __init__(self, IPAddr, crtlPort, key=None):
        if key==Key(None):
            self.key = hash_str(IPAddr+":"+ctrlPort)
        else:
            self.key = key
        self.IPAddr = IPAddr
        self.ctrlPort = crtlPort

    def __str__(self):
        return self.IPAddr+":"+str(self.ctrlPort)+">"+str(self.key)


# Class
class Node():
    """This class represents the current node in the Chord Network"""


    def __init__(self, known=None):
        self.IPAddr = net_server.getHostIP()
        self.ctrlPort = 7229
        self.predecessor = None
        self.successor = None
        if TEST_MODE:
            self.key = generate_random_key()
        else:
            self.key = hash_str(self.IPAddr+":"+str(self.ctrlPort))
        self.myinfo = Node_Info(self.IPAddr, self.ctrlPort, self.key)
        self.finger = []
        for i in range(1,KEY_SIZE+1):
            self.finger.append(None)
        self.net = None

    def attach_to_network(self, network):
        self.net = network
        return handle_message
    def __eq__(self, other):
        if (self.key == other.key and self.IPAddr == other.IPAddr and self.ctrlPort == other.ctrlPort):
            return True
        return False

    # must we modify for asynchronus networking magic?
    # no, lets look at the netlogo code.
    def find_successor(self, key):
        if between(key, self.key, self.successor.key):
            return self.successor
        else:
            closest = closest_preceding_node(key)
            #closest =  actual node
            return closest.find_successor(key)

    # search the finger table for the highest predessor for key
    def closest_preceding_node(self,key):
        for i in reversed(self.finger[1:]): # or should it be range(KEY_SIZE - 1, -1, -1))
            if i != None: 
                if between(i.key, self.key, key): #Stoica's paper indexes at 1, not 0
                    return i
        return self

    
    # create a new Chord ring.
    def create(self):
        self.predecessor = None
        self.successor = self

    # join node other's ring
    # this we need to modify for asynchronus stuff 
    def join(self, other):
        self.predecessor = None
        self.successor = other.find_successor(self.key)
    
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
thisNode.key = hash_str(str(uuid.uuid4()) + str(uuid.uuid4()))
thisNode.IPAddr = net_server.getHostIP()
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
