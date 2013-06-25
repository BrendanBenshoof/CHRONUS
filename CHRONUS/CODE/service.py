from message import *
from hash_util import *
import node
class Service(object):
    """This object is intented to act as a parent/promise for Service Objects"""
    def __init__(self):
        self.service_id = None
        self.callback = None
        self.owner = None

    def attach(self, owner, callback):
        """Called when the service is attached to the node"""
        """Should return the ID that the node will see on messages to pass it"""
        self.callback = callback
        self.owner = owner
        return self.service_id

    def handle_message(self, msg):
        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        return msg.service == self.service_id

    def send_message(self, msg, dest):
        self.callback(msg, dest)



class Internal_Service(Service):
    """Handler of Chord behavoir and internal messages"""
    def __init__(self):
        super(Service, self).__init__()
        self.service_id = INTERNAL
    
    def handle_message(self, msg):
        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        ##switch based on "type"
        msgtype = msg.get_content("type")
        response = None
        if msgtype == FIND:
            response = Update_Message(self.owner, msg.return_node.key, self.owner, msg.finger)
        elif msgtype == UPDATE:
            node.update_finger(msg.return_node, msg.finger)
        elif msgtype == STABILIZE:
            response = Stablize_Reply_Message(self.owner, msg.return_node.key, node.predecessor)
        elif msgtype == STABILIZE_REPLY:
            node.stabalize(msg)
        elif msgtype == NOTIFY:
            node.get_notified(msg)
        elif msgtype == CHECK_PREDECESSOR:
            response = Update_Message(self.owner, msg.return_node.key, self.owner, 0)
        else:
            return False
        if response != None:
            self.callback(response,msg.return_node)
        return True
            
