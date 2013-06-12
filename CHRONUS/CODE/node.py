#pulled from Benjamin Evans's implementation "pyChordDHT"
### TODO ###
# Finish stabilization
# hash math - some indexes are wrong <- I think this is fixed
# if request times out - use backup node
# update request on node failure
# Not closing connection properly - why?
############

class Node():
    """This class is primarily for holding info on 
    other nodes in the network"""
    ID = 0
    IPAddr = getHostIP()
    ctrlPort = 7228
    relayPort = 7229

    def __eq__(self, other):
        if (self.ID == other.ID and self.IPAddr == other.IPAddr and self.ctrlPort
            == other.ctrlPort and self.relayPort == other.relayPort):

            return True
        return False


####################### Globals #######################

#Node
thisNode = Node()
thisNode.ID = hash_str(str(uuid.uuid4()) + str(uuid.uuid4()))
thisNode.IPAddr = getHostIP()
thisNode.ctrlPort = 7228
thisNode.relayPort = 7229

prevNode = thisNode

#Finger table
fingerTable = []
fingerTableLock = Lock()
prevNodeLock = Lock()
numFingerErrors = 0

successorList = []
sucListLock = Lock()
successorOfflineAttempts = 0

#services
services =  {}


#Network connections
servCtrl = None
servRelay = None

