from message import *
from hash_util import *
import node

IRM =  "IRM"

class IRM_Service(Service):
    """ This is a complete and total replacement for the Internal_Service Class based on"""
    def __init__(self, db_service):
        super(Service, self).__init__()
        self.service_id = IRM
        self.db_service = db_service
        self.polls = {}

    def handle_message(self, message):
        pass


class IRM_Message(Message):
    pass

class IRM_Poll(IRM_Message):
    pass

class IRM_Poll_Reply(IRM_Message):
    pass

