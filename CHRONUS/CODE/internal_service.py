
class ECHO_service(Service):
    def __init__(self, message_router):
        super(Service, self).__init__()
        self.message_router = message_router
        self.service_id = SERVICE_ECHO
        message_router.register_service(self.service_id, self)

    def handle_message(self, msg):
        if not msg.service == self.service_id:
            raise Exception("Mismatched service recipient for message.")

        for k in msg.contents.keys():
            print msg.get_content(k)


class Internal_Service(Service):
    """Handler of Chord behavoir and internal messages"""
    def __init__(self, message_router):
        super(Service, self).__init__()
        self.message_router = message_router
        self.service_id = SERVICE_INTERNAL
        message_router.register_service(self.service_id, self)

    def handle_message(self, msg):
        if not msg.service == self.service_id:
            raise Exception("Mismatched service recipient for message.")


        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        ## switch based on "type"
        msgtype = msg.type
        response = None
        if node.TEST_MODE:
            if msg.origin_node != node.thisNode:
                pass
                #print "Got " + str(msgtype) +  " from " + str(msg.origin_node)
        if msgtype == FIND:  # This might not ever happen with new changes
            response = Update_Message(self.owner, msg.reply_to.key, msg.finger)
        elif msgtype == UPDATE:
            node.update_finger(msg.reply_to, msg.finger)
        elif msgtype == STABILIZE:
            response = Stablize_Reply_Message(self.owner, msg.reply_to.key, node.predecessor)
        elif msgtype == STABILIZE_REPLY:
            node.stabilize(msg)
        elif msgtype == NOTIFY:
            node.get_notified(msg)
        elif msgtype == CHECK_PREDECESSOR:
            response = Update_Message(self.owner, msg.reply_to.key, 0)
        elif msgtype == POLITE_QUIT:
            node.peer_polite_exit(msg.reply_to)

        else:
            return False
        if response != None:
            self.callback(response, msg.reply_to)
        return True

class Node_Service(Service):
    """Interface to the outside world"""
    def __init__(self, message_router):
        super(Service, self).__init__()

        self.message_router = message_router  # should be in base class used by all services
        self.service_id = SERVICE_NODE
        message_router.register_service(self.service_id,self)

    def handle_message(self, msg):
        if not msg.service == self.service_id:
            raise Exception("Mismatched service recipient for message.")
