#currently just a test script
#eventually to be the startup scrip for CHRONUS

import database as db 
import network_handler as net
import hash_util as hash
from message import *
import node as node

myself = node.Node()
print myself.myinfo