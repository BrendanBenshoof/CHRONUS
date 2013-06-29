#!/usr/bin/env python

import database as db 
import network_handler as net
import hash_util as hash
from message import *
import node as node
import service as serve
from dummy_network import *
import random
import sys
import os
from threading import *

import Topology_Service

try:
    node.ctrlPort = int(sys.argv[1])
    node.IPAddr = "localhost"
    node.thisNode = node.Node_Info(node.IPAddr, node.ctrlPort)
    Internal_service = serve.Internal_Service()
    node.add_service(Internal_service)
    node.add_service(serve.ECHO_service())
    node.net_server = start(node.thisNode, node.handle_message)
    database = db.Database("F:\DATABASE")
    node.add_service(database)

    TOPO = Topology_Service.Topology()
    node.add_service(TOPO)

    if len(sys.argv) > 2:
        node_name = sys.argv[2]
        node_port = int(sys.argv[3])
        othernode = node.Node_Info(node_name, node_port)
        node.join(othernode)
        print node.thisNode
        print othernode
        #f = lambda : node.join(othernode)
        #t = Thread(target=f)
        #t.start()
    else:
        node.create()
        #t = Thread(target = node.create)
        #t.start()
    node.startup()
    while True:
        cmd = raw_input(">>")
        if cmd[:6] == "get f ":
            x = int(cmd[6:])
            print node.fingerTable[x]
        elif cmd == 'q' or cmd ==  'Q' :
            quit()
        elif cmd == 'g' or cmd == 'G':
            print "estimate:", node.estimate_ring_density()
        elif cmd[:4] == "get ":
            database.get_record(cmd[4:])
        elif cmd[:4] == "put ":
            arg_str = cmd[4:].split(' ',1)
            database.put_record(arg_str[0],arg_str[1])
        elif cmd == "plot":
            TOPO.start_inquery()
        else:
            print "successor  ", node.successor
            print "predecessor", node.predecessor
except KeyboardInterrupt:
    exit
