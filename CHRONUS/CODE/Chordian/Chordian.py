#!/usr/bin/env python
###Startup and commandline file

#allow any common modules to be imported
import sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))


from shelver_service import Shelver_Service
from echo_service import Echo_Service
from topology_service import Topology_Service
from file_service import File_Service
#from map_reduce_service import Map_Reduce_Service
from network_service import Network_Service
from node_service import Node_Service, Node_Info
from service_message import *
import random
import sys
from message_router import Message_Router
import json
from urllib2 import urlopen


class Chordian():
    """
    Chordian orchestrates the SOA as the central container and sets up message-passing and system-wide settings.
    Support for multiple peers within a single process is provided by making services agnostic by providing
    operations without service-level or global state.
    """
    def __init__(self):
        self.message_router = Message_Router()

        #### setup services here
        Shelver_Service(self.message_router)
        Echo_Service(self.message_router)
        Topology_Service(self.message_router)
        File_Service(self.message_router)
#        Map_Reduce_Service(self.message_router)
        Network_Service(self.message_router)
        Node_Service(self.message_router)

    def attach_console(self):
        self.message_router.attach_console()

    def setup_node(self, public_ip, local_ip, local_port, seeded_peers ):
        self.message_router.route(Message_Setup_Node(public_ip, local_ip, local_port, seeded_peers))

    def test_local(self, node_count):
        nodes = []

        public_ip = "127.0.0.1"
        port_start = 19000
        for i in range(0,node_count):
            # emulate do/while -- seed with someone random that isn't me
            seed_port = i
            while seed_port == i and node_count > 1:
                seed_port = random.randint(0,node_count - 1)

            nodes.append((public_ip, "", port_start + i, [Node_Info(public_ip, port_start+ seed_port)] if node_count > 1 else []))

        for n in nodes:
            public_ip, local_ip, local_port, seeded_peers = n
            self.setup_node( public_ip, local_ip, local_port, seeded_peers)

def main():
    args = sys.argv
    local_port = int(args[1]) if len(args) > 1 else random.randint(9000, 9999)
    other_IP = args[2] if len(args) > 2 else None
    other_port = int(args[3]) if len(args) > 3 else None
    local_mode=True
    local_ip = ""  # bind to all interfaces

    public_ip = "127.0.0.1"

    if not local_mode:
        public_ip = json.load(urlopen('http://httpbin.org/ip'))['origin']
        print "just got my public ip:", public_ip

    seeded_peers = []
    if not other_IP is None and not other_port is None:
        seeded_peers.append( Node_Info(other_IP, other_port) )

    peer_coordinator = Chordian()
    peer_coordinator.test_local(2)  # 2 nodes
    #peer_coordinator.setup_node(public_ip, local_ip, local_port, seeded_peers)
    peer_coordinator.attach_console() # allow us to send k/b commands
if __name__ == "__main__":
    main()


