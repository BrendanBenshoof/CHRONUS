#Message object Abstraction for CHRONOS application
import pickle
from constants import *
from hash_util import *
import cPickle

#this is an abstract parent class
#you could use it, but it would be boring

FIND = "FIND"
UPDATE =  "UPDATE"
STABILIZE = "STABILIZE"
STABILIZE_REPLY = "STABILIZE_REPLY"
NOTIFY = "NOTIFY"
CHECK_PREDECESSOR = "CHECK_PREDECESSOR"
POLITE_QUIT = "POLITE_QUIT"
FAILURE = "FAILURE"

class Message(object):
    def __init__(self, service, type, success_callback_msg = None, failed_callback_msg = None):
        self.origin_node = None     # One hop origin
        self.destination_key = generate_random_key()    # 160 number or hash object
        self.reply_to = None        # Node to reply to
        self.contents = {}          # All other data
        self.service = service      # What service handles this
        self.dest_service = service
        self.type = type
        self.success_callback_msg = success_callback_msg
        self.failed_callback_msg = failed_callback_msg
        self.finger = None          # int -1 to 160


    @staticmethod
    def deserialize(in_string):
        try:
            return cPickle.loads(in_string) # pickle.loads(in_string)
        except EOFError:
            fail_message = Message()
            fail_message.service = FAILURE
            return fail_message
        #there are soo many exceptions I should be catching here

    def serialize(self):
        #it would be great if this was encrypted
        #would could also fix this with using a public-key algorithim for p2p communication
        # return pickle.dumps(self)
        return cPickle.dumps(self)

    def add_content(self, key, data):
        self.contents[key] = data

    def get_content(self, key):
        to_return = None
        try:
            to_return = self.contents[key]
        except IndexError:
            print "get_content was asked to look for a non-existant key"
        return to_return

class Find_Successor_Message(Message):
    @classmethod
    def Type(cls): return FIND

    def __init__(self, origin_node, destination_key, requester, finger = 1):
        Message.__init__(self, SERVICE_NODE, Find_Successor_Message.Type())
        self.origin_node = origin_node  # node that just sent this message
        self.destination_key = destination_key  # the key we're trying to find the node responsible for
        self.reply_to = requester
        self.finger = finger

class Update_Message(Message):
    @classmethod
    def Type(cls): return UPDATE

    def __init__(self, origin_node, destination_key, finger):
        Message.__init__(self, SERVICE_NODE, Update_Message.Type())
        self.origin_node = origin_node
        self.destination_key = destination_key  #key we are sending it back to
        self.finger = finger        # entry in the finger table to update.
        self.reply_to = origin_node     # the node to connect to


class Stablize_Message(Message):
    @classmethod
    def Type(cls): return STABILIZE

    """docstring for Stablize_Message"""
    def __init__(self, origin_node, successor):
        Message.__init__(self, SERVICE_NODE, Stablize_Message.Type( ))
        self.origin_node = origin_node
        self.destination_key = successor.key
        self.reply_to = origin_node

class Stabilize_Reply_Message(Message):
    @classmethod
    def Type(cls): return STABILIZE_REPLY

    """docstring for Stablize_Reply_Message"""
    def __init__(self, origin_node, destination_key, predecessor):
        Message.__init__(self, SERVICE_NODE, Stabilize_Reply_Message.Type())
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.predecessor =  predecessor
        self.reply_to = origin_node

class Notify_Message(Message):
    @classmethod
    def Type(cls): return NOTIFY

    """docstring for Notify_Message"""
    def __init__(self, origin_node,destination_key):
        Message.__init__(self, SERVICE_NODE, Notify_Message.Type())
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.reply_to = origin_node

class Check_Predecessor_Message(Message):
    @classmethod
    def Type(cls): return CHECK_PREDECESSOR

    def __init__(self, origin_node,destination_key):
        Message.__init__(self, SERVICE_NODE, Check_Predecessor_Message.Type())
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.reply_to = origin_node

class Exit_Message(Message):
    @classmethod
    def Type(cls): return POLITE_QUIT

    """docstring for Notify_Message"""
    def __init__(self, origin_node, destination_key):
        Message.__init__(self, SERVICE_NODE, Exit_Message.Type())
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.reply_to = origin_node


"""
Internal Messages
"""


class Message_Internal(object):
    def __init__(self, dest_service, type, success_callback_msg=None, failed_callback_msg=None):
        self.dest_service = dest_service
        self.type = type
        self.success_callback_msg = success_callback_msg
        self.failed_callback_msg = failed_callback_msg

class Message_Console_Command(Message_Internal):
    @classmethod
    def Type(cls): return "MESSAGE_CONSOLE_COMMAND"

    def __init__(self, service_id, command, args=[], console_node=None):
        super(Message_Console_Command, self).__init__(service_id, Message_Console_Command.Type())
        self.command = command
        self.args = args  # dictionary of args
        self.console_node = console_node


# Messages specific to Network_Service

class Message_Start_Server(Message_Internal):
    @classmethod
    def Type(cls): return "MESSAGE_START_SERVER"

    def __init__(self, host_ip, host_port, success_callback_msg=None, failed_callback_msg=None):
        super(Message_Start_Server, self).__init__(SERVICE_NETWORK, Message_Start_Server.Type(), success_callback_msg, failed_callback_msg)
        self.host_ip = host_ip
        self.host_port = host_port

class Message_Start_Server_Callback(Message_Internal):
    @classmethod
    def Type(cls): return "MESSAGE_START_SERVER_CALLBACK"

    def __init__(self, dest_service, node, result, success_callback_msg=None, failed_callback_msg=None):
        super(Message_Start_Server_Callback, self).__init__(dest_service, Message_Start_Server_Callback.Type(), success_callback_msg, failed_callback_msg)
        self.result = result
        self.node = node

class Message_Stop_Server(Message_Internal):
    @classmethod
    def Type(cls): return "MESSAGE_STOP_SERVER"

    def __init__(self, success_callback_msg=None, failed_callback_msg=None):
        super(Message_Stop_Server, self).__init__(SERVICE_NETWORK, Message_Stop_Server.Type(), success_callback_msg, failed_callback_msg)

class Message_Stop_Server_Callback(Message_Internal):
    @classmethod
    def Type(cls): return "MESSAGE_STOP_SERVER_CALLBACK"

    def __init__(self, dest_service, node, result, success_callback_msg=None, failed_callback_msg=None):
        super(Message_Stop_Server_Callback, self).__init__(dest_service, Message_Stop_Server_Callback.Type(), success_callback_msg, failed_callback_msg)
        self.result = result
        self.node = node

class Message_Send_Peer_Data(Message_Internal):
    @classmethod
    def Type(cls): return "MESSAGE_SEND_PEER_DATA"

    def __init__(self, node, network_msg, success_callback_msg=None, failed_callback_msg=None):
        super(Message_Send_Peer_Data, self).__init__(SERVICE_NETWORK, Message_Send_Peer_Data.Type(), success_callback_msg, failed_callback_msg)
        self.remote_ip = node.IPAddr
        self.remote_port = node.ctrlPort
        self.network_msg = network_msg

class Message_Forward(Message_Internal):
    @classmethod
    def Type(cls): return "MESSAGE_FORWARD"

    def __init__(self, origin_node, forward_hash, forward_msg, success_callback_msg=None, failed_callback_msg=None):
        super(Message_Forward, self).__init__(SERVICE_NODE, Message_Forward.Type(), success_callback_msg, failed_callback_msg)
        self.origin_node = origin_node
        self.forward_hash = forward_hash
        self.forward_msg = forward_msg

# Messages specific to Node_Service
class Message_Setup_Node(Message_Internal):
    @classmethod
    def Type(cls): return "MESSAGE_SETUP_NODE"

    def __init__(self, public_ip, local_ip, local_port, seeded_peers, success_callback_msg=None, failed_callback_msg=None):
        super(Message_Setup_Node, self).__init__(SERVICE_NODE, Message_Setup_Node.Type(),
            success_callback_msg, failed_callback_msg)
        self.public_ip = public_ip
        self.local_ip = local_ip
        self.local_port = local_port
        self.seeded_peers = seeded_peers

class Message_Recv_Peer_Data(Message_Internal):
    @classmethod
    def Type(cls): return "MESSAGE_RECV_PEER_DATA"

    def __init__(self, local_ip, local_port, raw_data, success_callback_msg=None, failed_callback_msg=None):
        super(Message_Recv_Peer_Data, self).__init__(SERVICE_NODE, Message_Recv_Peer_Data.Type(), success_callback_msg, failed_callback_msg)
        self.local_ip = local_ip
        self.local_port = local_port
        self.network_msg = Message.deserialize(raw_data)

GET = "GET"
PUT = "PUT"
DATABASE = "DATABASE"
RESPONSE = "RESP"

class Database_Put_Message(Message):
    @classmethod
    def Type(cls): return PUT

    def __init__(self, origin_node, destination_key, keyfile_hash, file_contents, success_callback_msg=None, failed_callback_msg=None):
        super(Database_Put_Message,self).__init__(SERVICE_SHELVER, Database_Put_Message.Type( ),
                                                  success_callback_msg, failed_callback_msg)
        self.origin_node = origin_node
        self.storage_node = self.origin_node # default to local (will be overwritten by final dest if better ideal forward)
        self.destination_key = destination_key
        self.keyfile_hash = keyfile_hash
        self.file_contents = file_contents

class Database_Put_Message_Response(Message):
    @classmethod
    def Type(cls): return "Database_Put_Message_Response"

    def __init__(self, origin_node, storage_node, destination_key, keyfile_hash, success_callback_msg=None, failed_callback_msg=None):
        super(Database_Put_Message_Response,self).__init__(SERVICE_FILE, Database_Put_Message_Response.Type( ),
                                                  success_callback_msg, failed_callback_msg)
        self.origin_node = origin_node
        self.storage_node = storage_node
        self.keyfile_hash = keyfile_hash
        self.destination_key = destination_key

class Database_Get_Message(Message):
    @classmethod
    def Type(cls): return GET

    def __init__(self, origin_node, destination_key, success_callback_msg=None, failed_callback_msg=None):
        super(Database_Get_Message,self).__init__(SERVICE_SHELVER, Database_Get_Message.Type( ),
                                                  success_callback_msg, failed_callback_msg)
        self.origin_node = origin_node
        self.storage_node = None  # set by receiving Node_Service if no more forwarding
        self.destination_key = destination_key

class Database_Get_Message_Response(Message):
    @classmethod
    def Type(cls): return RESPONSE

    def __init__(self, origin_node, storage_node,destination_key, file_contents, success_callback_msg=None, failed_callback_msg=None):
        super(Database_Get_Message_Response,self).__init__(SERVICE_FILE, Database_Get_Message_Response.Type( ),
                                                  success_callback_msg, failed_callback_msg)
        self.origin_node = origin_node
        self.storage_node = storage_node
        self.destination_key = destination_key
        self.file_contents = file_contents

class Database_Backup_Message(Message):
    @classmethod
    def Type(cls): return "BACKUP"

    def __init__(self, origin_node, backup_pile):
        Message.__init__(self, SERVICE_SHELVER, "BACKUP")
        self.origin_node = origin_node
        self.add_content("backup",backup_pile)
        self.reply_to = origin_node
