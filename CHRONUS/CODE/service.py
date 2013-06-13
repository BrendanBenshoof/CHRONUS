from message import *
from hash_util import *
class Service(object):
    """This object is intented to act as a parent/promise for Service Objects"""
    def __init__(self):
        self.service_id = None
        self.callback = None

    def attach(self, callback):
        """Called when the service is attached to the node"""
        """Should return the ID that the node will see on messages to pass it"""
        self.callback = callback
        return self.service_id

    def handle_message(self, msg):
        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        return msg.service == self.service_id

    def send_message(self, msg, dest):
        self.callback(msg, dest)
        