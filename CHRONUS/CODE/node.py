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
TEST_MODE = False   #duh
VERBOSE = True      # True for various debug messages, False for a more silent execution.
net_server = None
MAINTENANCE_PERIOD = 2.0

class Node_Info():
    """This is struct containing the info of other nodes.  
    We use this, rather than the node class itself, for entries in the finger table
    as well as successor and predecessor.   
    """
    def __init__(self, IPAddr, ctrlPort, key=None):
        if key is None:
            self.key = hash_str(IPAddr+":"+str(ctrlPort))
        else:
            self.key = key
        self.IPAddr = IPAddr
        self.ctrlPort = ctrlPort
        ##print self.IPAddr, self.ctrlPort, str(self.key)

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

    def __str__(self):
        return str(self.IPAddr)+":"+str(self.ctrlPort)+":"+str(self.key)
        
        
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
predecessor_lock = Lock()

successor = None
successor_lock = Lock()

#Finger table
fingerTable = None
fingerTable_lock = Lock()
#numFingerErrors = 0
next_finger = 0

#services
services = {}
services_lock = Lock()


#Network connections
servCtrl = None
servRelay = None

###########
# Find successor
###########

#  This is find successor and find closest predecessor rolled into one.
def find_ideal_forward(key):
    ##print key
    if successor != None and hash_between_right_inclusive(key, thisNode.key, successor.key):
        return successor
    return closest_preceding_node(key)



def closest_preceding_node(key):
    for finger in reversed(fingerTable[1:]): # or should it be range(KEY_SIZE - 1, -1, -1))
        if finger != None: 
            if hash_between(finger.key, thisNode.key, key): #Stoica's paper indexes at 1, not 0
                return finger   #this could be the source of our problem;  how do we distinguish between him being repsonsible and him preceding
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
    predecessor = thisNode
    successor = thisNode
    fingerTable = [thisNode, successor]  
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
    predecessor = thisNode
    successor = thisNode
    fingerTable = [thisNode, successor]  
    for i in range(2,KEY_SIZE+1):
        fingerTable.append(None)
    find = Find_Successor_Message(thisNode, thisNode.key, thisNode)
    send_message(find, node)
#########We shoudl clean this up    
def startup():
    if TEST_MODE:
        print "Startup"
    t = Thread(target=kickstart)
    t.setDaemon(True)
    t.start()
    print "New thread started!"

def kickstart():
    if TEST_MODE:
        print "Kickstart"
    begin_stabilize()
    while True:
        time.sleep(MAINTENANCE_PERIOD)
        begin_stabilize()
        time.sleep(MAINTENANCE_PERIOD)
        begin_stabilize()
        check_predecessor()        
        time.sleep(MAINTENANCE_PERIOD)
        fix_fingers(10)

##END CLEANUP


#############
# Maintenence
#############

# called periodically. n asks the successor
# about its predecessor, verifies if n's immediate
# successor is consistent, and tells the successor about n

def begin_stabilize():
    if TEST_MODE:
        print "Begin Stabilize"
    message = Stablize_Message(thisNode,successor)
    send_message(message, successor)
    
# need to account for successor being unreachable
def stabilize(message):
    global successor
    successor_lock.acquire(True)            
    if TEST_MODE:
        print "Stabilize"
    x = message.get_content("predecessor")
    if x!=None and hash_between(x.key, thisNode.key, successor.key):
        successor = x
    send_message(Notify_Message(thisNode, successor.key))
    successor_lock.release()
            

# TODO: Call this function
# we couldn't reach our successor;
# He's dead, Jim.
# goto next item in the finger table
# TODO: if pred is thisNode. 
def stabilize_failed():
    global fingerTable
    global successor
    fingerTable_lock.acquire(True)
    successor_lock.acquire(True)
    if TEST_MODE:
        print "Stabilize Failed"
    for entry in fingerTable[2:]:
        if entry != None:
            successor = entry
            fingerTable[1] = entry
            begin_stabilize()
            fingerTable_lock.release()
            successor_lock.release()
            return
    fingerTable_lock.release()
    successor_lock.release()
            
    #what to do here???

# we were notified by node other;
# other thinks it might be our predecessor
# TODO: if pred is thisNode.
def get_notified(message):
    global predecessor
    global fingerTable
    if TEST_MODE:
        print "Get Notified"
    other =  message.origin_node
    if(predecessor == thisNode or hash_between(other.key, predecessor.key, thisNode.key)):
        fingerTable_lock.acquire(True)
        predecessor_lock.acquire(True)
        predecessor = other
        fingerTable[0] = predecessor
        fingerTable_lock.release()
        predecessor_lock.release()
        for s in services.values():
            s.change_in_responsibility(predecessor.key, thisNode.key)


def fix_fingers(n=1):
    global next_finger
    for i in range(0,n):
        if successor != thisNode and predecessor != thisNode:
            next_finger = next_finger + 1
            if next_finger > KEY_SIZE:
                next_finger = 1
            if TEST_MODE:
                print "Fix Fingers + " + str(next_finger)
            target_key = add_keys(thisNode.key, generate_key_with_index(next_finger-1))
            message = Find_Successor_Message(thisNode, target_key, thisNode, next_finger)
            send_message(message)

def update_finger(newNode,finger):
    global fingerTable
    global successor
    global predecessor
    predecessor_lock.acquire(True)
    successor_lock.acquire(True)
    fingerTable_lock.acquire(True)
    if TEST_MODE:
        print "Update finger: " + str(finger)
    fingerTable[finger] = newNode
    fingerTable_lock.release()
    if finger == 1:
        successor = newNode
    elif finger == 0:
        predecessor = newNode
    successor_lock.release()
    predecessor_lock.release()

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

"""
Our problem is that there are three scenarios for handling the message, not 2
1) I'm responsible
2) I'm not responsible, but I know who is (ie, the successor)
3) I don't know, but I know who else to ask

Our problem, I think, is we were cludging together 1 and 2 and 2 and 3
"""
def handle_message(msg):

    if hash_between_right_inclusive(msg.destination_key, predecessor.key, thisNode.key):   # if I'm responsible for this key
        try:
            myservice = services[msg.service]
        except KeyError:
            return
        myservice.handle_message(msg)
    else:
        forward_message(msg)

def forward_message(message):
    if hash_between_right_inclusive(message.destination_key, thisNode.key, successor.key):
        message.origin_node = thisNode
        if TEST_MODE:
            print "not mine; forwarding to " + str(successor)
        send_message(message, successor)
    else:
        closest =  closest_preceding_node(message.destination_key)
        if TEST_MODE:
            print "not mine; forwarding to " + str(closest)
        if closest==thisNode:
            if TEST_MODE:
                print "I'm the closest, how did that happen"
        else:
            message.origin_node = thisNode
            send_message(message, closest)

def estimate_ring_density():
    total = 0
    i = 80
    count = 0
    for f in fingerTable[80:]:
        if not f is None:
            ideal = int(generate_key_with_index(i).key, 16)
            actual = int(f.key.key, 16)
            distance = actual-ideal
            total += distance*2
            i+=1
            count +=1
    average = total/count
    ring_size = 0x01 << 160
    return ring_size / average
    

def message_failed(msg, intended_dest):
    for i in range(0,160)[::-1]:
        if fingerTable[i] == intended_dest:
            if i == 1: #we lost our successor
                fingerTable[1] = thiNode
                fingerTable[1] = find_ideal_forward(thisNode.key)
                successor = fingerTable[1] 
            if i == 0: #we lost our predecessor
                fingerTable[0] = thisNode
                print "THIS SHOULD NOT HAPPEN. PANIC NOW"
                if fingerTable[-1] is None:
                    predecessor_lock.acquire(True)
                    predecessor = thisNode
                    predecessor_lock.release()
                else:
                    predecessor_lock.acquire(True)
                    predecessor = fingerTable[-1]
                    predecessor_lock.release()
                    fingerTable[0] = fingerTable[-1]
            else: #we just lost a finger
                fingerTable[i] = None #cut it off properly
    send_message(msg)

def peer_polite_exit(leaveing_node):
    print "peer leaving"
    global predecessor
    global successor
    global fingerTable
    fingerTable_lock.acquire(True)
    for i in range(0,160)[::-1]:
        if fingerTable[i] == leaveing_node:
            if i == 1: #we lost our successor
                fingerTable[1] = thisNode
                fingerTable[1] = find_ideal_forward(thisNode.key)
                successor_lock.acquire(True)
                successor = fingerTable[1] 
                successor_lock.release()
            if i == 0: #we lost our predecessor
                fingerTable[0] = thisNode
                print "My sucessor dropped out"
                predecessor = thisNode

            else: #we just lost a finger
                fingerTable[i] = None #cut it off properly
    fingerTable_lock.release()                

def my_polite_exit():
    done = []
    for p in fingerTable:
        if not p is None:
            quitMSG = Exit_Message(thisNode, p.key)
            send_message(quitMSG,p)
            done.append(p)


""" 
Don't mind this, I lost my train of thought, maybe it will come back.


So here is the problem that influnences EVERYTHING, and that is how other services are going to find the responsible node.
    You see, there are assumptions, and we need to be on the same page.

    First, we need to figure out who decides who is responsible for what.  Right now, the psuedocode assumes other peopple decide you are responsible for something via find_successor

    Assume for the sake of argument, we are now using a file storage service and we are trying to find where to put files.

    Alice (on a different node than thisNode) has file 'X', which is Bob's node.  thisNode might or might not be Bob's.  She wants to find the node where to store it.  Obviously, it would be inefficient to pass the file all around the network until it got to the right place, so she has to find the corresponing node first.  This means she sends a lookup thru the network and gets the node connection info, then connects for the file deposit.



    Scenario 1:  thisNode gets Alice's lookup request.  ThisNode is Bob's. Execept in a very small network, it is very rare the message.destination_key and thisNode.key match.
    this is because if you are the successor of X, someone would have sent that information back to Alice.

    Scenario 2: thisNode 


    One  way to handle this whole issue is to add a function to messages called create_reply, which will take in thisNode, and create the reply for you
"""
