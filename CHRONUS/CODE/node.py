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
TEST_MODE = False   #self explanitory here
VERBOSE = True      # True for various debug messages, False for a more silent execution.

class Node_Info():
    """This is struct containing the info of other nodes.  
    We use this, rather than the node class itself, for entries in the finger table
    as well as successor and predecessor.   
    """
    def __init__(self, IPAddr, crtlPort, key=None, successor=None):
        if successor == None:
            successor = self
        if Key(None)==key:
            self.key = hash_str(IPAddr+":"+ctrlPort)
        else:
            self.key = key
        self.IPAddr = IPAddr
        self.ctrlPort = crtlPort
        self.successor = successor

    def __str__(self):
        return self.IPAddr+":"+str(self.ctrlPort)+">"+str(self.key)

# Class
class Node():
    """This class represents the current node in the Chord Network.
    We try to follow Stoica et al's scheme as closely as possible here,
    except their methods aren't asynchronus.  Our changes are listed below
    
    1.  Like Stoica et al, finger[1] is the successor. This keeps the math identical.
        However, lists index beginning at 0, so finger[0] is used to store the predecessor
    2.  To call functions on other nodes, we pass them a message, like in the case of notify().
        We don't have the other node's node object available to us, so we send it a message
        which will make the node call notify()
    """
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
        self.finger = [self.successor]  
        for i in range(1,KEY_SIZE+1):
            self.finger.append(None)
        self.net = None
        self.next = 0 # next finger to check

    def attach_to_network(self, network):
        self.net = network
        return handle_message

    def __eq__(self, other):
        if (self.key == other.key and self.IPAddr == other.IPAddr and self.ctrlPort == other.ctrlPort):
            return True
        return False



 
    

    
    # call after getting the message
    def get_join_success(self, message, successor):
        #Possible security, spam join messages for other people
        self.successor = successor
        self.finger[1] = successor #TODO: check if this conflicts with finger maintenence


    def finish_stabalize(self, Sucessors_pred):
            if hash_between(Sucessors_pred.key, self.key, self.successor.key):
                self.successor = Sucessors_pred
            self.successor.notify(self)
    
    #other said he may be my predecessor
    def notify(self,other):
        if self.predecessor == None or hash_between(other.key, self.predecessor.key, self.key):
            self.predecessor = other
    
    # Called periodically
    # Updates the finger table
    # TODO: async  the last line of this sucker
    def fix_fingers(self):
        self.next = self.next + 1
        if self.next > KEY_SIZE:
            self.next = 1
        find_successor(add_keys(self.key + generate_key_with_index(2**next - 1)))



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

predecessor =None
successor = None

#services
services =  {}


#Network connections
servCtrl = None
servRelay = None


def find_successor(message):
    global thisNode
    global successor
    key = message.get_content("key")    
    if hash_between_right_inclusive(key, thisNode.key, successor.key):
        destination =  message.get_content("requester")
        origin = thisNode
        connectTo = successor  # Tell the node to conenct to my successor
        update = Update_Message(origin, destination, key, connectTo) 
        send_message(update)
        #edge case dest = myself?
    else:
        closest = closest_preceding_node(key) # TODO: what if closest is self? update with info myself?
        if closest == thisNode:
            destination =  message.get_content("requester")
            origin = thisNode
            connectTo = thisNode  # Tell the node to conenct to my successor
            update = Update_Message(origin, destination, key, connectTo) 
            send_message(update)  # if we get logic errors and can't find stuff, it's because of thise
        message.origin_node = thisNode
        message.dest = destination
        send_message(message)

# search the finger table for the highest predecessor for key
def closest_preceding_node(key):
    for n in reversed(finger[1:]): # or should it be range(KEY_SIZE - 1, -1, -1))
        if n != None: 
            if hash_between(n.key, thisNode.key, key): #Stoica's paper indexes at 1, not 0
                return n
    return thisNode


    
# create a new Chord ring.
# TODO: finger table?
def create():
    global successor
    global predecessor
    predecessor = None
    successor = thisNode

# join node node's ring
# TODO: finger table?
# this we need to modify for asynchronus stuff 
def join(node):
    global thisNode
    global predecessor
    predecessor = None
    find =  Find_Successor_Message(origin_node, node,origin_node,origin_node.key)
    send_message(find)

# TODO:  Async
# called periodically. n asks the successor
# about its predecessor, verifies if n's immediate
# successor is consistent, and tells the successor about n
def begin_stabalize():
    message = Stabilize_Message(thisNode,successor)
    send_message(message)

# need to account for sucessor being unreachable
def stabalize(message):
    x = message.get_content("predecessor")
    if hash_between(x.key, thisNode.key, successor.key):
        global successor
        successor = x
    send_message(Notify_Message(thisNode,successor))

# we couldn't reach our sucessor;
# He's dead, Jim.
# goto next item in the finger table
def stabalize_failed():
    pass

# we were notified by node other;
# other thinks it might be our predecessor
def get_notified(message):
    global predecessor
    global finger
    other =  message.origin_node
    if(predecessor == None or hash_between(other.key,predecessor.key, thisNode.key) or predecessor==thisNode):
        predecessor = other
        finger[0] = predecessor


def fix_fingers():
    global thisNode
    global finger
    global successor
    global predecessor


# ping our predecessor.  pred = nil if no response
def check_predecessor():
    pass
   
#politely leave the network 
def exit():
    pass


def switchboard(message):
    best_destination = closest_preceding_node(message.key) 
    if best_destination == thisNode:
        handle_message(message)
    else:
        



###############################
# Service Code
###############################


def add_service(service, callback):
    services[service.attach(callback)] = service
    if VERBOSE: 
        print "Service " + service.service_id + "attached" 

def send_message(msg, destination):
    #TODO: write something to actually test this
    net_server.send_message(msg.serialize(), destination)

# called when node is passed a message
def handle_message(msg, origin):
    pass
