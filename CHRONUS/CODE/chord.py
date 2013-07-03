#!/usr/bin/env python
###Startup and commandline file
import service
import shelver as db 
import Topology_Service
import hash_util
import random
import dummy_network
import node

from threading import *
import sys
import message_router
import network_service
from message import Message_Start_Server
from message_router import Message_Router
from globals import *

# backwards-compatibility use of global vars...encapsulation is easily
# possible by ensuring all functionality lives in a service with a reference
# to router which would then be instantiated in main()
services = {}
commands = {}

def add_service(service_object):
    s_name = service_object.service_id
    services[s_name] = service_object

def attach_services():
    for s_name in services.keys():
        node.add_service(services[s_name])
        commands_list = services[s_name].attach_to_console()
        if not commands_list is None:
            for c in commands_list:
                commands[c] = services[s_name]

def setup_Node(addr="localhost", port=None):
    node.IPAddr = addr
    node.ctrlPort = port
    node.thisNode = node.Node_Info(node.IPAddr, node.ctrlPort)
    #node.net_server = dummy_network.start(node.thisNode, node.handle_message)

    #### setup services here
    add_service(network_service.Network_Service(Message_Router.instance()))
    add_service(service.Node_Service(Message_Router.instance()))
    add_service(service.Internal_Service(Message_Router.instance()))
    add_service(service.ECHO_service(Message_Router.instance()))
    add_service(Topology_Service.Topology(Message_Router.instance()))
    add_service(db.Shelver(Message_Router.instance(),"test.db"))
    ####
    attach_services()

    # send service start messages
    Message_Router.instance().route(Message_Start_Server(addr, port))

def join_ring(node_name, node_port):
    othernode = node.Node_Info(node_name, node_port)
    node.join(othernode)

def no_join():
    node.create()

def console():
    cmd = "-"
    try:
        cmd = raw_input()
    except EOFError: #the user does not have a terminal
        pass
    while not ( cmd == "q" or cmd == "Q"):
        command, args = None, None
        splitted = cmd.split(' ',1)
        if len(splitted) >= 1:
            command = splitted[0]
        if len(splitted) == 2:
            args = splitted[1]
        if command in commands.keys():
            commands[command].handle_command(command, args)
        elif cmd != "-":
            print "successor", node.successor
            print "predecessor", node.predecessor
        try:
            cmd = raw_input()
        except EOFError: #the user does not have a terminal
            pass

def main():
    global router
    args = sys.argv
    local_port = int(args[1]) if len(args) > 1 else random.randint(9000, 9999)
    other_IP = int(args[2]) if len(args) > 2 else None
    other_port = int(args[3]) if len(args) > 3 else None

    setup_Node(port=local_port)
    if not other_IP is None and not other_port is None:
        join_ring(other_IP, other_port)
    else:
        no_join()
    node.startup()
    console()

if __name__ == "__main__":
    main()

