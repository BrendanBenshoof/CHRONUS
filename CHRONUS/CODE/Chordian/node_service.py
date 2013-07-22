#pulled from Benjamin Evans's implementation "pyChordDHT"
### TODO ###
# Finish stabilization
# hash math - some indexes are wrong <- I think this is fixed
# if request times out - use backup node
# update request on node failure
# Not closing connection properly - why?
############
from collections import deque
import time
from threading import *
import multiprocessing
import sched
import os
from hash_util import *
from super_service import Service
from service_message import *
from asyncoro import Coro, AsynCoroThreadPool, logger
import logging

import sys

# Debug variables
TEST_MODE = False   #duh -- TO DO: NEED TO CHECK why maintenance stops sending network messages after Find_Successor!!!
VERBOSE = True      # True for various debug messages, False for a more silent execution.
MAINTENANCE_PERIOD = 10000

class Node_Info(object):
    """This is struct containing the info of other nodes.
    We use this, rather than the node class itself, for entries in the finger table
    as well as successor and predecessor.
    """
    def __init__(self, IPAddr, ctrlPort, successor=None, predecessor=None, key=None):
        if key is None:
            self.key = hash_str(IPAddr+":"+str(ctrlPort))
        else:
            self.key = key
            
        self.successor = successor
        self.predecessor = predecessor
        self.IPAddr = IPAddr
        self.ctrlPort = ctrlPort
        ##print self.IPAddr, self.ctrlPort, str(self.thisNode.key)

    def __eq__(self,other):
        if other == None:
            return False
        return self.key == other.key

    def __ne__(self,other):
        if other == None:
            return True
        return not self.key == other.key

    def print_key(self): return str(self.IPAddr)+":"+str(self.ctrlPort) +":"+str(self.key)

    def __str__(self):
        return str(self.IPAddr)+":"+str(self.ctrlPort)


"""This class represents the current node in the Chord Network.
We try to follow Stoica et al's scheme as closely as possible here,
except their methods aren't asynchronus.  Our changes are listed below

1.  Like Stoica et al, finger[1] is the successor. This keeps the math identical.
    However, lists index beginning at 0, so finger[0] is used to store the predecessor
2.  To call functions on other nodes, we pass them a message, like in the case of notify().
    We don't have the other node's node object available to us, so we send it a message
    which will make the node call notify()
"""
class Node_Service(Service):
    exit = False
    pause_scheduler = False

    def __init__(self, message_router):
        super(Node_Service, self).__init__(SERVICE_NODE, message_router, cl_name="ns")
        self.exit = False
        self.pause_scheduler = False
        self.nodes = {}
        self.queue = deque()
        self.delay_queue = deque()

        self.scheduler_thread = Thread(target=self._thread_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

        self._stabilize_coro = Coro(self._coro_stabilize)

    def delay_enqueue(self,message,ms):
        self.delay_queue.append( (time.time(), ms, message))

    def _thread_scheduler(self):
        try:
            while not self.exit:
                requeue = deque()

                while len(self.delay_queue) > 0 and not self.exit:
                    queued_at, delay_ms, message = self.delay_queue.popleft()
                    if (queued_at + delay_ms / 1000) < time.time():
                        #self.enqueue(message)
                        self._stabilize_coro.send(message)
                    else:
                        requeue.append((queued_at, delay_ms, message))

                while len(requeue) > 0 and not self.exit:
                    self.delay_queue.append(requeue.popleft())

                time.sleep(5)  # 10 ms
        except:
            show_error()
        print "Scheduler thread exiting"

    def _coro_stabilize(self, coro=None):
        coro.set_daemon()

        thread_pool = AsynCoroThreadPool(2 * multiprocessing.cpu_count())
        while not self.exit:
            try:
                command, context = yield self._stabilize_coro.receive()

                if self.exit:  # fast exit for now (non-graceful)
                    break

                #command, context = self.queue.popleft()
                if self.pause_scheduler or context.join_on_stabilize:  # just cycle the messages until unpaused
                    if context.join_on_stabilize:
                        context.send_message(Find_Successor_Message(context.thisNode, context.thisNode.key, context.thisNode), context.join_on_stabilize)
                        context.join_on_stabilize = None
                        delay = MAINTENANCE_PERIOD * 3
                    else:
                        delay = MAINTENANCE_PERIOD

                    self.delay_enqueue((command,context), delay)
                    continue


                if command == "NODE_STABILIZE":
                    yield thread_pool.async_task(coro, context.begin_stabilize)
                elif command == "NODE_CHECK_PREDECESSOR":
                    yield thread_pool.async_task(coro, context.check_predecessor)
                elif command == "NODE_FIX_FINGERS":
                    yield thread_pool.async_task(coro, context.fix_fingers, 10)
            except:
                show_error()

        print "Coro(stabilize) exiting"


    def stop(self, context=None):
        self.exit = True
        self._stabilize_coro.send((None,None))
        #for i in range(2 * multiprocessing.cpu_count()):
            #self.queue.append(('terminate', context))
            #self.signal_item_queued.set()

    def get_console_node(self):
        if len(self.nodes) > 0:
            return self.nodes[self.nodes.keys()[0]]

    def handle_message(self, msg):
        if not msg.dest_service == self.service_id:
            raise Exception("Mismatched service recipient for message.")

        if msg.type == Message_Setup_Node.Type():
            node = Node(self, msg.public_ip, msg.local_ip, msg.local_port)
            if msg.seeded_peers:
                for peer in msg.seeded_peers:
                    node.join(peer) # use callback to try next peer if join fails (join is async)
            else:
                node.join()

            self.message_router.route(
                Message_Start_Server(node.local_ip, node.local_port,
                        Message_Start_Server_Callback(self.service_id, node, True),
                        Message_Start_Server_Callback(self.service_id, node, False)))

        elif msg.type == Message_Start_Server_Callback.Type():
            if msg.result:
                self.nodes[str(msg.node)] = msg.node
                self.delay_enqueue(("NODE_STABILIZE", msg.node), 1000)
            else:
                msg.node.exit_network()
                print "Unable to successfully start server for node at " + msg.node.local_ip + ":" + str(msg.node.local_port)
        if msg.type == Message_Forward.Type( ):
            ni = msg.origin_node
            if self.nodes.has_key(str(ni)):
                lnode = self.nodes[str(ni)] # get the Node class this message is addressed to (ip:port)
                forward_node = lnode.find_ideal_forward(msg.forward_hash)

                if forward_node != ni:
                    self.send_message(msg.forward_msg, forward_node)
                else:
                    self.send_message(msg.forward_msg)
        elif msg.type == Message_Recv_Peer_Data.Type(): # came off the wire
            ni = Node_Info(msg.local_ip if len(msg.local_ip) > 0 else "127.0.0.1",msg.local_port)
            if self.nodes.has_key(str(ni)):
                lnode = self.nodes[str(ni)] # get the Node class this message is addressed to (ip:port)

                msg = msg.network_msg
                logger.debug(str(ni) + " received network msg: " + msg.type)

                if msg.type == Message_Forward.Type( ):
                    lnode.find_ideal_forward(msg.forward_hash) #fix this...we need to do forward the message
                elif msg.type == Find_Successor_Message.Type():
                    self.send_message(Update_Message(lnode.thisNode, msg.reply_to.key, msg.finger), msg.reply_to)
                elif msg.type == Update_Message.Type( ):
                    lnode.update_finger(msg.reply_to, msg.finger)
                elif msg.type == Check_Predecessor_Message.Type():
                    self.send_message(Update_Message(lnode.thisNode, msg.reply_to.key, 0), msg.reply_to)
                elif msg.type == Stablize_Message.Type( ):
                    self.send_message(Stabilize_Reply_Message(lnode.thisNode, msg.reply_to.key, msg.reply_to))
                elif msg.type == Stabilize_Reply_Message.Type():
                    lnode._coro_stabilize(msg)
                elif msg.type == Notify_Message.Type():
                    lnode.get_notified(msg)
                elif msg.type == Exit_Message.Type():
                    lnode.peer_polite_exit(msg.reply_to)
                elif msg.type == Database_Put_Message.Type() or msg.type == Database_Get_Message.Type():
                    msg.storage_node = lnode.thisNode
                    self.message_router.route(msg)
                elif msg.type == Database_Put_Message_Response.Type() or msg.type == Database_Get_Message_Response.Type():
                    self.message_router.route(msg)


        elif msg.type == Message_Console_Command.Type():
            self.handle_command(msg.command,msg.args)

    # wraps message in network packet if not destined for local
    #def route_node_message(self,msg):
    #    if self.nodes.has_key(str(msg.origin_node)):
    #        node = self.nodes[str(msg.origin_node)]
    #        forward_to = node.find_ideal_forward(msg.destination_key)
    #        if forward_to == node:
    #            self.send_message(msg)
    #        else:
    #            self.send_message(Message_Send_Peer_Data(forward_to, msg.serialize()))

    def handle_command(self,cmd,args=[]):
        if cmd == "print":
            for node in self.nodes.values():
                print "successor  ", node.thisNode.successor.print_key()
                print "predecessor", node.thisNode.predecessor.print_key()
        elif cmd == "pause":
            self.pause_scheduler = True
        elif cmd == "resume":
            self.pause_scheduler = False


class Node():
    def __str__(self):
        return str(self.thisNode)

    #delay join until first stabilize
    join_on_stabilize = None

    def __init__(self, node_service, public_ip, local_ip="127.0.0.1", local_port=7228, key=None):
        self.thisNode = Node_Info(public_ip,local_port, key)
        self.key = self.thisNode.key
        self.node_service = node_service
        self.local_ip = local_ip
        self.local_port = local_port

        self.predecessor_lock = Lock()
        self.successor_lock = Lock()
        
        #Finger table
        self.fingerTable = None
        self.fingerTable_lock = Lock()
        #numFingerErrors = 0
        self.next_finger = 0

            
    ###########
    # Find self.successor
    ###########
    
    #  This is find self.thisNode.successorand find closest self.thisNode.predecessor rolled into one.
    def find_ideal_forward(self,key):
        ##print self.thisNode.key
        if self.thisNode.successor != None and hash_between_right_inclusive(key, self.thisNode.key, self.thisNode.successor.key):
            return self.thisNode.successor
        return self.closest_preceding_node(self.thisNode.key)
    
    
    
    def closest_preceding_node(self,key):
        for finger in reversed(self.fingerTable[1:]): # or should it be range(KEY_SIZE - 1, -1, -1))
            if finger != None:
                if hash_between(finger.key, self.thisNode.key, key): #Stoica's paper indexes at 1, not 0
                    return finger   #this could be the source of our problem;  how do we distinguish between him being repsonsible and him preceding
        return self.thisNode
    
    
    ######
    # Ring and Node Creation
    ######

    # join node node's ring
    # TODO: finger table?   CHeck to refactor
    # this we need to modify for asynchronus stuff
    def join(self, node=None):
        if TEST_MODE:
            print "Join" if node else "Create"

        self.thisNode.predecessor = self.thisNode
        self.thisNode.successor= self.thisNode
        self.fingerTable = [self.thisNode, self.thisNode]
        for i in range(2,KEY_SIZE+1):
            self.fingerTable.append(None)

        self.join_on_stabilize = node

    #############
    # Maintenence
    #############
    
    # called periodically. n asks the self.successor
    # about its self.predecessor, verifies if n's immediate
    # self.thisNode.successoris consistent, and tells the self.thisNode.successorabout n
    
    def begin_stabilize(self):
        try:
            if TEST_MODE:
                print "Begin Stabilize (" + str(self) + ")"
            if self.thisNode.successor != self.thisNode:
                self.send_message(Stablize_Message(self.thisNode,self.thisNode.successor), self.thisNode.successor)
            else:  # short-circuit message loop/network if it's self-addressed
                self.stabilize(Stabilize_Reply_Message(self.thisNode, self.thisNode.key, self.thisNode))
        finally:  # moved enqueue here to ensure we don't attempt to scheduling until we've completed a cycle
            self.node_service.delay_enqueue( ("NODE_CHECK_PREDECESSOR", self), MAINTENANCE_PERIOD)

    # need to account for self.thisNode.successor being unreachable
    def stabilize(self,message):
        self.successor_lock.acquire(True)
        if TEST_MODE:
            print "Stabilize (" + str(self.thisNode) + ")"
        x = message.predecessor
        if x!=None and hash_between(x.key, self.thisNode.key, self.thisNode.successor.key):
            self.thisNode.successor = x

        if self.thisNode != self.thisNode.successor:
            self.send_message(Notify_Message(self.thisNode, self.thisNode.successor.key))
        else:  # short-circuit message loop/network if it's self-addressed
            self.get_notified(Notify_Message(self.thisNode, self.thisNode.successor.key))

        self.successor_lock.release()
    
    
    # TODO: Call this function
    # we couldn't reach our self.successor;
    # He's dead, Jim.
    # goto next item in the finger table
    # TODO: if pred is self.
    def stabilize_failed(self):
        self.fingerTable_lock.acquire(True)
        self.successor_lock.acquire(True)
        if TEST_MODE:
            print "Stabilize Failed"
        for entry in self.fingerTable[2:]:
            if entry != None:
                self.thisNode.successor= entry
                self.fingerTable[1] = entry
                self.begin_stabilize()
                self.fingerTable_lock.release()
                self.successor_lock.release()
                return
        self.fingerTable_lock.release()
        self.successor_lock.release()
    
        #what to do here???
    
    # we were notified by node other;
    # other thinks it might be our self.predecessor
    # TODO: if pred is self.
    def get_notified(self,message):
        if TEST_MODE:
            print "Get Notified (" + str(self.thisNode) + ")"
        other =  message.origin_node
        if(self.thisNode.predecessor == self.thisNode or hash_between(other.key, self.thisNode.predecessor.key, self.thisNode.key)):
            self.fingerTable_lock.acquire(True)
            self.predecessor_lock.acquire(True)
            self.thisNode.predecessor = other
            self.fingerTable[0] = self.thisNode.predecessor
            self.fingerTable_lock.release()
            self.predecessor_lock.release()

            # Actually does nothing (except for perhaps file manager so why call for all services...send File_Service a message)
            #for s in services.values():
            #    s.change_in_responsibility(self.thisNode.predecessor.key, self.thisNode.key)
    
    
    def fix_fingers(self,n=1):
        try:
            if TEST_MODE:
                print "Fix Fingers (" + str(self.thisNode) + ")"
            for i in range(0,n):
                if self.thisNode.successor!= self.thisNode and self.thisNode.predecessor != self.thisNode:
                    self.next_finger = self.next_finger + 1
                    if self.next_finger > KEY_SIZE:
                        self.next_finger = 1
                    if TEST_MODE:
                        print "Fix Fingers + " + str(self.next_finger)
                    target_key = add_keys(self.thisNode.key, generate_key_with_index(self.next_finger-1))

                    dest_node = self.find_ideal_forward(target_key)
                    if dest_node != self.thisNode:
                        message = Find_Successor_Message(self.thisNode, target_key, self.thisNode, self.next_finger)
                        self.send_message(message, dest_node)
                    else:  # short-circuit message loop/network if it's self-addressed
                        self.update_finger(self.thisNode, self.next_finger)
        finally:  # moved enqueue here to ensure we don't attempt to scheduling until we've completed a cycle
            self.node_service.delay_enqueue( ("NODE_STABILIZE", self), MAINTENANCE_PERIOD)

    def update_finger(self,newNode,finger):
        self.predecessor_lock.acquire(True)
        self.successor_lock.acquire(True)
        self.fingerTable_lock.acquire(True)
        if TEST_MODE:
            print "Update finger " + str(finger) + ":  (" + str(self.thisNode) + ")"
        self.fingerTable[finger] = newNode
        self.fingerTable_lock.release()
        if finger == 1:
            self.thisNode.successor= newNode
        elif finger == 0:
            self.thisNode.predecessor = newNode
        self.successor_lock.release()
        self.predecessor_lock.release()
    
    # ping our self.thisNode.predecessor.  pred = nil if no response
    def check_predecessor(self):
        try:

            if TEST_MODE:
                print "Check Predecessor (" + str(self.thisNode) + ")"
            if(self.thisNode.predecessor != None):  # do this here or before it's called
                dest_node = self.find_ideal_forward(self.thisNode.predecessor.key)
                if dest_node != self.thisNode:
                    self.send_message(Check_Predecessor_Message(self.thisNode, self.thisNode.predecessor.key),dest_node)
                else:  # short-circuit message loop/network if it's self-addressed
                    self.update_finger(self.thisNode, 0)
        finally:  # moved enqueue here to ensure we don't attempt to scheduling until we've completed a cycle
            self.node_service.delay_enqueue( ("NODE_FIX_FINGERS", self), MAINTENANCE_PERIOD )

    #politely leave the network
    def exit_network(self):
        pass
    
    
    ###############################
    # Service Code
    ###############################

    
    def send_message(self, msg, destination=None):
        if destination == None:
            destination = self.find_ideal_forward(msg.destination_key)

        if destination == self.thisNode and msg.dest_service == SERVICE_NODE:
            #  self.node_service.send_message(msg)
            raise "This is silly -- caller should just invoke method directly to bypass messaging/network"
        else:  #network-bound message
            self.node_service.send_message(msg, destination)
    
    # called when node is passed a message
    
    """
    Our problem is that there are three scenarios for handling the message, not 2
    1) I'm responsible
    2) I'm not responsible, but I know who is (ie, the self.successor)
    3) I don't know, but I know who else to ask
    
    Our problem, I think, is we were cludging together 1 and 2 and 2 and 3
    """
    def handle_message(self,msg):
        if hash_between_right_inclusive(msg.destination_key, self.thisNode.predecessor.key, self.thisNode.key):   # if I'm responsible for this self.thisNode.key
            self.message_router.route(msg)
        else:
            self.forward_message(msg)
    
    def forward_message(self,message):
        if hash_between_right_inclusive(message.destination_key, self.thisNode.key, self.thisNode.successor.key):
            message.origin_node = self.thisNode
            if TEST_MODE:
                print "not mine; forwarding to " + str(self.successor)
            self.send_message(message, self.successor)
        else:
            closest = self.closest_preceding_node(message.destination_key)
            if TEST_MODE:
                print "not mine; forwarding to " + str(closest)
            if closest==self.thisNode:
                if TEST_MODE:
                    print "I'm the closest, how did that happen"
            else:
                message.origin_node = self.thisNode
                self.send_message(message, closest)
    
    def estimate_ring_density(self):
        total = 0
        i = 80
        count = 0
        for f in self.fingerTable[80:]:
            if not f is None:
                ideal = int(self.generate_key_with_index(i).key, 16)
                actual = int(f.key.key, 16)
                distance = actual-ideal
                total += distance*2
                i+=1
                count +=1
        average = total/count
        ring_size = 0x01 << 160
        return ring_size / average
    
    
    def message_failed(self,msg, intended_dest):
        print "message failed"
        print msg, intended_dest
        salvage_sucessor = False
        for i in range(0,160)[::-1]:
            if not self.fingerTable[i] is None:
                if self.fingerTable[i].IPAddr == intended_dest.IPAddr and self.fingerTable[i].ctrlPort == intended_dest.ctrlPort:
                    if i == 1: #we lost our successor
                        self.fingerTable[1] = self.thisNode
                        #fingerTable[1] = find_ideal_forward(thisNode.key)
                        self.successor_lock.acquire(True)
                        self.thisNode.successor= self.thisNode
                        print "new sucessor", self.successor
                        salvage_sucessor = True
                        self.successor_lock.release()
                    elif i == 0: #we lost our predecessor
                        self.fingerTable[0] = self.thisNode
                        self.predecessor_lock.acquire(True)
                        predecessor = self.thisNode
                        self.predecessor_lock.release()

                    else: #we just lost a finger
                        print "lost finger",i
                        self.fingerTable[i] = None #cut it off properly
        if salvage_sucessor:
            for i in range(1,160):
                if not self.fingerTable[i] is None:
                        self.successor_lock.acquire(True)
                        successor = self.fingerTable[i]
                        self.successor_lock.release()
    
    def peer_polite_exit(self,leaving_node):
        print "peer leaving"
        self.fingerTable_lock.acquire(True)
        for i in range(0,160)[::-1]:
            if self.fingerTable[i] == leaving_node:
                if i == 1: #we lost our self.successor
                    self.fingerTable[1] = self.thisNode
                    self.fingerTable[1] = self.find_ideal_forward()
                    self.successor_lock.acquire(True)
                    self.thisNode.successor= self.fingerTable[1]
                    self.successor_lock.release()
                if i == 0: #we lost our self.predecessor
                    self.fingerTable[0] = self.thisNode
                    print "My sucessor dropped out"
                    self.thisNode.predecessor = self.thisNode
    
                else: #we just lost a finger
                    self.fingerTable[i] = None #cut it off properly
        self.fingerTable_lock.release()
    
    def my_polite_exit(self):
        done = []
        for p in self.fingerTable:
            if not p is None:
                quitMSG = Exit_Message(self.thisNode, p.key)
                self.send_message(quitMSG,p)
                done.append(p)
    
    
    """
    Don't mind this, I lost my train of thought, maybe it will come back.
    
    
    So here is the problem that influnences EVERYTHING, and that is how other services are going to find the responsible node.
        You see, there are assumptions, and we need to be on the same page.
    
        First, we need to figure out who decides who is responsible for what.  Right now, the psuedocode assumes other peopple decide you are responsible for something via find_successor
    
        Assume for the sake of argument, we are now using a file storage service and we are trying to find where to put files.
    
        Alice (on a different node than self) has file 'X', which is Bob's node.  self might or might not be Bob's.  She wants to find the node where to store it.  Obviously, it would be inefficient to pass the file all around the network until it got to the right place, so she has to find the corresponing node first.  This means she sends a lookup thru the network and gets the node connection info, then connects for the file deposit.
    
    
    
        Scenario 1:  self gets Alice's lookup request.  ThisNode is Bob's. Execept in a very small network, it is very rare the message.destination_key and self.thisNode.key match.
        this is because if you are the self.thisNode.successorof X, someone would have sent that information back to Alice.
    
        Scenario 2: self
    
    
        One  way to handle this whole issue is to add a function to messages called create_reply, which will take in self, and create the reply for you
    """
