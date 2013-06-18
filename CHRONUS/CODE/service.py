from message import *
from hash_util import *
class Service(object):
    """This object is intented to act as a parent/promise for Service Objects"""
    def __init__(self):
        self.service_id = None
        self.callback = None
        self.owner = None

    def attach(self, callback, owner):
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



class Find_Service(object):
    """docstring for Find_Service"""
    def __init__(self, arg):
        super(Find_Service, self).__init__()
        self.arg = arg
        