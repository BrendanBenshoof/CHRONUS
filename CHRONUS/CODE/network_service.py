from service import Service
from message import Message
from network_constant import Service_Type, Message_Type
from peer_zero import Peer_Zero_Server, Peer_Zero_Client

# messages specific to Network_Service are placed here for now but should be moved
# into message.py

class Message_Start_Server(Message):
    def __init__(self, callback, host_ip, host_port):
        Message.__init__(self)
        self.type = Message_Type.START_SERVER
        self.service = Service_Type.NETWORK_SERVICE
        self.callback = callback
        self.host_ip = host_ip
        self.host_port = host_port

class Message_Stop_Server(Message):
    def __init__(self, callback):
        Message.__init__(self)
        self.type = Message_Type.STOP_SERVER
        self.service = Service_Type.NETWORK_SERVICE
        self.callback = callback


class Message_Send_Peer_Data(Message):
    def __init__(self, callback, remote_ip, remote_port, raw_data):
        Message.__init__(self)
        self.type = Message_Type.SEND_PEER_DATA
        self.service = Service_Type.NETWORK_SERVICE
        self.callback = callback  # formed response message (when "complete" notification is desired)
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.raw_data = raw_data


class Network_Service(Service):
    """Interface to the outside world"""
    def __init__(self, message_router):
        super(Service, self).__init__()

        self.message_router = message_router  # should be in base class used by all services
        self._clients = {}

        self._server = None
        self.service_id = Service_Type.NETWORK_SERVICE
        message_router.register_service(self.service_id,self)

    def handle_message(self, msg):
        if not msg.service == self.service_id:
            raise "Mismatched service recipient for message."

        if msg.type == Message_Type.START_SERVER:
            if not self._server:
                self._server = Peer_Zero_Server(self, msg.host_ip, msg.host_port)
        elif msg.type == Message_Type.STOP_SERVER:
            if self._server:
                self._server.stop(msg)
        elif msg.type == Message_Type.SEND_PEER_DATA:
            client = Peer_Zero_Client(self, msg.remote_ip, msg.remote_port)
            self._clients[msg.remote_ip + ":" + msg.remote_port] = client
            client.send(msg.data, (msg,client))
        elif msg.type == Message_Type.DISCONNECT_PEER:
            client = self.clients[msg.remote_ip + ":" + msg.remote_port]
            if client:
                client.stop((msg, client))

    def on_server_start(self, context):
        # TODO: possibly route messages to anyone who cares and wants to clean up when
        # the server has shut down
        return None

    def on_server_stop(self, context):
        # TODO: possibly route messages to anyone who cares and wants to clean up when
        # the server has shut down
        return None

    def on_peer_connected(self, context):
        # TODO: possibly route messages to anyone who cares and wants to clean up when
        # a node is no longer connected
        return None

    def on_peer_disconnected(self, context):
        # TODO: possibly route messages to anyone who cares and wants to clean up when
        # a node is no longer connected
        msg, client = context
        if self.clients[msg.remote_ip + ":" + msg.remote_port]:
            del self._connected_clients[msg.remote_ip + ":" + msg.remote_port]
        return None

    def on_peer_data_received(self, context):
        # TODO: buffer until a complete message is received then pass to
        # router.route(complete_message)
        return None

    def on_peer_data_sent(self, context):
        msg, client = context
        # TODO: Send a message to the person who requested data sent to let them know send was successful
        # e.g. if router.route( msg.callback ) where notify_completion_message is
        #      formed by the caller in the original message as an "event" notification

        if msg.callback:
            # could provide some info like msg.callback.property = value but prob unnecessary
            self.message_router.route(msg.callback)
        return None






