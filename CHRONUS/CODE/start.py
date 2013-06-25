#currently just a test script
#eventually to be the startup scrip for CHRONUS

import database as db 
import network_handler as net
import hash_util as hash
from message import *
import node as node
import service as serve
from dummy_network import *
import random
import sys

try:
	node.ctrlPort = int(sys.argv[1])
	node.IPAddr = "localhost"
	node.create()
	Internal_service = serve.Internal_Service()
	node.add_service(Internal_service)
	node.net_server = start(node.thisNode, node.handle_message)
	node.startup()
	if len(sys.argv) > 2:
		node_name = sys.argv[2]
		node_port = int(sys.argv[3])
		othernode = node.Node_Info(node_name, node_port)
		node.join(othernode)
	else:
		node.join(node.thisNode)
except KeyboardInterrupt:
	exit
