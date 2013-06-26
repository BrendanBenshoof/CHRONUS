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
from message import *
#import dummy_network as  


# Debug variables
TEST_MODE = True   #duh
VERBOSE = True      # True for various debug messages, False for a more silent execution.
net_server = None
MAINTENANCE_PERIOD = 3.0

class Node_Info():
    """This is struct containing the info of other nodes.  
    We use this, rather than the node class itself, for entries in the finger table
    as well as successor and predecessor.   
    """
    def __init__(self, IPAddr, crtlPort, key=None):
        if key is None:
            self.key = hash_str(IPAddr+":"+str(crtlPort))
        else:
            self.key = key
        self.IPAddr = IPAddr
        self.ctrlPort = crtlPort
        print self.IPAddr, self.ctrlPort, str(self.key)

    def __str__(self):
        return self.IPAddr+":"+str(self.ctrlPort)+">"+str(self.key)
    
    def __eq__(self,other):
        if other == None:
            return False
        return self.key == other.key
        
    def __ne__(self,other):
        if other == None:
            return True
        return not self.key == other.key
        
        
"""This class represents the current node in the Chord Network.
We try to follow Stoica et al's scheme as closely as possible here,
except their methods aren't asynchronus.  Our changes are listed below

1.  Like Stoica et al, finger[1] is the successor. This keeps the math identical.
    However, lists index beginning at 0, so finger[0] is used to store the predecessor
2.  To call functions on other nodes, we pass them a message, like in the case of notify().
    We don't have the other node's node object available to us, so we send it a message
    which will make the node call notify()
"""

thisNode = None
IPAddr = ""
ctrlPort = 7228
key = ""

predecessor= None
successor = None

#Finger table
fingerTable = None
#numFingerErrors = 0
next_finger = 0

#services
services =  {}


#Network connections
servCtrl = None
servRelay = None

###########
# Find successor
###########

#  This is find successor and find closest predecessor rolled into one.
def find_ideal_forward(key):
    #print key
    if successor != None and hash_between_right_inclusive(key, thisNode.key, successor.key):
        return successor
    for n in reversed(fingerTable[1:]): # or should it be range(KEY_SIZE - 1, -1, -1))
        if n != None: 
            if hash_between(n.key, thisNode.key, key): #Stoica's paper indexes at 1, not 0
                return n
    return thisNode


######
# Ring and Node Creation
######


# create a new Chord ring.
# TODO: finger table?
def create():
    global successor, predecessor, fingerTable, key, thisNode
    if TEST_MODE:
        print "Create"
    key = thisNode.key
    predecessor = None
    successor = thisNode
    fingerTable = [None, successor]  
    for i in range(2,KEY_SIZE+1):
        fingerTable.append(None)


# join node node's ring
# TODO: finger table?   CHeck to refactor
# this we need to modify for asynchronus stuff 
def join(node):
    global predecessor
    global fingerTable
    global successor
    if TEST_MODE:
        print "Join"
    predecessor = None
    successor = node
    fingerTable = [None, successor]  
    for i in range(2,KEY_SIZE+1):
        fingerTable.append(None)
    find = Find_Successor_Message(thisNode, thisNode.key, thisNode)
    send_message(find, successor)
    
def establish_network(network):
    net_server = network


def startup():
    if TEST_MODE:
        print "Startup"
    t = Thread(target=kickstart)
    t.start()
    print "New thread started!"

def kickstart():
    if TEST_MODE:
        print "Kickstart"
    begin_stabalize()
    while True:
        time.sleep(MAINTENANCE_PERIOD)
        fix_fingers()
        time.sleep(MAINTENANCE_PERIOD)
        fix_fingers()
        time.sleep(MAINTENANCE_PERIOD)
        fix_fingers()
        time.sleep(MAINTENANCE_PERIOD)
        begin_stabalize()



#############
# Maintenence
#############

# called periodically. n asks the successor
# about its predecessor, verifies if n's immediate
# successor is consistent, and tells the successor about n

def begin_stabalize():
    if TEST_MODE:
        print "Begin Stabilize"
    message = Stablize_Message(thisNode,successor)
    send_message(message, successor)
    
# need to account for successor being unreachable
def stabalize(message):
    global successor
    if TEST_MODE:
        print "Stabilize"
    x = message.get_content("predecessor")
    if x!=None and hash_between(x.key, thisNode.key, successor.key):
        successor = x
    send_message(Notify_Message(thisNode,successor.key))

# TODO: Call this function
# we couldn't reach our successor;
# He's dead, Jim.
# goto next item in the finger table
def stabalize_failed():
    global fingerTable
    global successor
    if TEST_MODE:
        print "Stabilize Failed"
    for entry in fingerTable[2:]:
        if entry != None:
            successor = entry
            fingerTable[1] = entry
            begin_stabalize()
            return
    #what to do here???

# we were notified by node other;
# other thinks it might be our predecessor
def get_notified(message):
    global predecessor
    global fingerTable
    if TEST_MODE:
        print "Get Notified"
    other =  message.origin_node
    if(predecessor == None or hash_between(other.key, predecessor.key, thisNode.key)):
        predecessor = other
        fingerTable[0] = predecessor

def fix_fingers():
    global next_finger
    if successor != None and predecessor != None:
        next_finger = next_finger + 1
        if next_finger > KEY_SIZE:
            next_finger = 1
        if TEST_MODE:
            print "Fix Fingers + " + str(next_finger)
        target_key = add_keys(thisNode.key, generate_key_with_index(2**(next_finger-1)))
        message = Find_Successor_Message(thisNode, target_key, thisNode, next_finger)
        send_message(message)

def update_finger(newNode,finger):
    global fingerTable
    global successor
    global predecessor
    global predecessor
    if TEST_MODE:
        print "Update finger: " + str(finger)
    fingerTable[finger] = newNode
    if finger == 1:
        successor = newNode
    elif finger == 0:
        predecessor = newNode
    

# ping our predecessor.  pred = nil if no response
def check_predecessor():
    if(predecessor != None):  # do this here or before it's called
        send_message(Check_Predecessor_Message(thisNode, predecessor.key),predecessor)
   
#politely leave the network 
def exit_network():
    pass


###############################
# Service Code
###############################


def add_service(service):
    global services
    global thisNode
    services[service.attach(thisNode, send_message)] = service
    if VERBOSE: 
        print "Service " + service.service_id + "attached" 

def send_message(msg, destination=None):
    #TODO: write something to actually test this
    if destination == None:
        destination = find_ideal_forward(msg.destination_key)
    net_server.send_message(msg, destination)

# called when node is passed a message
def handle_message(msg):
    """Need to fix this.  Say I'm node 1, and my message is looking to find key 2, and node 3 is my successor.  
    So.  I go thru my finger table, checking each finger in turn to see if it's between me and the key, finally we get to finger[1] (3).  
    3 is between 1 and 3, so we return me being the closest preceding node (which is correct)
    But the assumption here is that get_dest = me means that I'm responsible for key 2 (I'm not)"""
    get_dest = thisNode
    if not msg.destination_key == thisNode.key:
        get_dest = find_ideal_forward(msg.destination_key)
    if TEST_MODE:
        #print "Message "  + str(msg)  + " has get_dest = " + str(get_dest) 
        pass
    if not get_dest == thisNode:
        print "not mine; forwarding"
        print get_dest
        print thisNode
        msg.origin_node = thisNode
        send_message(msg, get_dest)
    else:
        try:
            myservice = services[msg.service]
        except IndexError:
            return
        myservice.handle_message(msg)
