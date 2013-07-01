#!/usr/bin/env python
###Startup and commandline file
import service
import shelver as db 
import Topology_Service
import hash_util as hash
import random
import dummy_network
import node

from threading import *
import sys

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
    if port is None:
        port = random.randint(9000,9999)
    node.ctrlPort = port
    node.thisNode = node.Node_Info(node.IPAddr, node.ctrlPort)
    node.net_server = dummy_network.start(node.thisNode, node.handle_message)
    #### setup services here
    add_service(service.Internal_Service())
    add_service(service.ECHO_service())
    add_service(Topology_Service.Topology())
    add_service(db.Shelver("test.db"))
    ####
    attach_services()

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
    args = sys.argv
    local_port = None
    other_IP = None
    other_port = None
    for i in range(0,len(args)):
        if i == 1:
            local_port = int(args[i])
        if i == 2:
            other_IP = args[i]
        if i == 3:
            other_port = args[i]
    setup_Node(port = local_port)
    if not other_IP is None and not other_port is None:
        join_ring(other_IP, other_port)
    else:
        no_join()
    node.startup()
    console()

if __name__ == "__main__":
    main()
