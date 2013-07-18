from service_message import *

class Service(object):
    """This object is intended to act as a parent/promise for Service Objects"""
    def __init__(self,
                 service_id,  # message passing identifier
                 message_router,  # central-dispatch
                 #callback=None, owner=None,
                 cl_name=None  # shorthand for CL testing
                 ):
        self.service_id = service_id
        self.message_router = message_router
        self.message_router.register_service(self.service_id,self)
        #self.callback = callback
        #self.owner = owner
        self.cl_name = cl_name

    # this has been super-ceded by messages
    #def attach(self, owner, callback):
    #    """Called when the service is attached to the node"""
    #    """Should return the ID that the node will see on messages to pass it"""
    #    self.callback = callback
    #    self.owner = owner
    #    return self.service_id

    def handle_message(self, msg):
        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        #if not msg.service == self.service_id:
        #    raise "Mismatched service recipient for message."
        return msg.service == self.service_id

    def attach_to_console(self):
        ### return a list of command-strings
        return []

    # this has been changed to a message Message_Console_Command
    #def handle_command(self, comand_st, arg_str):
    #    ### one of your commands got typed in
    #    return None

    def send_message(self, msg, dest=None):
        if not dest:
            self.message_router.route(msg)
        else:
            self.message_router.route(Message_Send_Peer_Data(dest, msg.serialize()))


    # this should be a message sent to services that need to change or sent as a broadcast message
    # if all services need to possibly take action
    #def change_in_responsibility(self,new_pred_key, my_key):
    #    pass #this is called when a new, closer predicessor is found and we need to re-allocate
    #        #responsibilties




