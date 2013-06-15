#currently just a test script
#eventually to be the startup scrip for CHRONUS

import database as db 
import network_handler as net
import hash_util as hash
from message import *
import node as node
from dummy_network import *

myself = node.Node()
print myself.myinfo

Dummy = Dummy_Network()
Dummy.add_node(myself.attach_to_network(Dummy))

