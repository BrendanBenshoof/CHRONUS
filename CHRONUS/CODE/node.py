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
TEST_MODE = False   #duh
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

"""This class represents the current node in the Chord Network.
We try to follow Stoica et al's scheme as closely as possible here,
except their methods aren't asynchronus.  Our changes are listed below

1.  Like Stoica et al, finger[1] is the successor. This keeps the math identical.
    However, lists index beginning at 0, so finger[0] is used to store the predecessor
2.  To call functions on other nodes, we pass them a message, like in the case of notify().
    We don't have the other node's node object available to us, so we send it a message
    which will make the node call notify()
"""
#Node


IPAddr = ""
ctrlPort = 7228
key = ""

predecessor= None
successor = None

#Finger table
fingerTable = None
numFingerErrors = 0
nextFinger = 0


#services
services =  {}


#Network connections
servCtrl = None
servRelay = None

###########
# Find Sucessor
###########

#
def find_ideal_forward(key):
    if hash_between_right_inclusive(key, thisNode.key, sucessor.key):
        return sucessor
    for n in reversed(fingerTable[1:]): # or should it be range(KEY_SIZE - 1, -1, -1))
        if n != None: 
            if hash_between(n.key, thisNode.key, key): #Stoica's paper indexes at 1, not 0
                return n
    return thisNode

def handle_find_successor(message):
    """ Send an update message back across the ring """
    pass

def handle_update(message):
    pass

######
# Ring Creation
######


# create a new Chord ring.
# TODO: finger table?
def create():
    global successor, predecessor, fingerTable, key
    key = hash_str(IPAddr+":"+ctrlPort)
    predecessor = None
    thisNode = Node_Info(IPAddr, crtlPort, key, successor)
    successor = thisNode
    fingerTable = [successor]  
    for i in range(1,KEY_SIZE+1):
        fingerTable.append(None)

# join node node's ring
# TODO: finger table?
# this we need to modify for asynchronus stuff 
def join(node):
    global thisNode
    global predecessor
    predecessor = None
    find =  Find_Successor_Message(thisNode, thisNode.key,thisNode)
    send_message(find, node)





#############
# Maintenence
#############
    
# TODO:  Async
# called periodically. n asks the successor
# about its predecessor, verifies if n's immediate
# successor is consistent, and tells the successor about n
def begin_stabalize():
    message = Stabilize_Message(thisNode,successor)
    send_message(message)

# need to account for sucessor being unreachable
def stabalize(message):
    global successor
    x = message.get_content("predecessor")
    if hash_between(x.key, thisNode.key, successor.key):
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
    global predecessor, fingerTable
    other =  message.origin_node
    if(predecessor == None or hash_between(other.key,predecessor.key, thisNode.key) or predecessor==thisNode):
        predecessor = other
        fingerTable[0] = predecessor

def fix_fingers():
    global nextFinger
    nextFinger = nextFinger + 1
    if nextFinger > KEY_SIZE:
        nextFinger = 1
    target_key = add_keys(thisNode.key, generate_key_with_index(2**(nextFinger-1)))
    message = Find_Successor_Message(thisNode, target_key, thisNode, nextFinger)
    send_message(message)

def update_finger(newNode,finger):
    global fingerTable
    fingerTable[finger] = newNode
    if finger == 1:
        sucessor = newNode
    elif finger ==0:
        predecessor = newNode
    

# ping our predecessor.  pred = nil if no response
def check_predecessor():
    if(predecessor != None):  # do this here or before it's called
        send_message(Check_Predecessor_Message(thisNode, predecessor.key),predecessor)
   
#politely leave the network 
def exit():
    pass


###############################
# Service Code
###############################


def add_service(service, callback):
    global services
    services[service.attach(callback)] = service
    if VERBOSE: 
        print "Service " + service.service_id + "attached" 

def send_message(msg, destination=None):
    #TODO: write something to actually test this
    if destination == None:
        destination = find_ideal_forward(msg.destination_key)
    net_server.send_message(msg.serialize(), destination)

# called when node is passed a message
def handle_message(msg):
    """Need to fix this.  Say I'm node 1, and my message is looking to find key 2, and node 3 is my sucessor.  
    So.  I go thru my finger table, checking each finger in turn to see if it's between me and the key, finally we get to finger[1] (3).  
    3 is between 1 and 3, so we return me being the closest preceding node (which is correct)
    But the assumption here is that get_dest = me means that I'm responsible for key 2 (I'm not)"""
    get_dest = find_ideal_forward(msg.destination_key)  # do find sucessor instead, otherwise a sucessor will never actually get it
    if not get_dest == thisNode:
        msg.origin_node = thisNode
        send_message(msg, get_dest)
    else:
        try:
            myservice = services[msg.service]
        except IndexError:
            return
        myservice.handle_message(msg)
            
