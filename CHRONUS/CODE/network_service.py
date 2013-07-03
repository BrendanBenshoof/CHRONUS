from service import Service
from message import Message
from peer_local import Peer_Local
from peer_remote import Peer_Remote
from globals import *


class Network_Service(Service):
    """Interface to the outside world"""
    def __init__(self, message_router):
        super(Service, self).__init__()

        self.message_router = message_router  # should be in base class used by all services
        self.service_id = SERVICE_NETWORK
        message_router.register_service(self.service_id,self)

        self._clients = {}
        self._server = None

    def handle_message(self, msg):
        if not msg.service == self.service_id:
            raise Exception("Mismatched service recipient for message.")

        if msg.type == MESSAGE_START_SERVER:
            if not self._server:
                self._server = Peer_Local(self, msg.host_ip, msg.host_port)
        elif msg.type == MESSAGE_STOP_SERVER:
            if self._server:
                self._server.stop(msg)
        elif msg.type == MESSAGE_SEND_PEER_DATA:
            client = Peer_Remote(self, msg.remote_ip, msg.remote_port)
            self._clients[msg.remote_ip + ":" + str(msg.remote_port)] = client
            client.send(msg.raw_data, (msg,client))
        elif msg.type == MESSAGE_DISCONNECT_PEER:
            client = self.clients[msg.remote_ip + ":" + str(msg.remote_port)]
            if client:
                client.stop((msg, client))

    def on_server_start(self, context):
        # TODO: possibly route messages to anyone who cares and wants to clean up when
        # the server has shut down
        return None

    def on_server_stop(self, context):
        # TODO: possibly route messages to anyone who cares and wants to clean up when
        # the server has shut down
        self._server = None
        return None

    def on_peer_connected(self, context):
        # TODO: possibly route messages to anyone who cares and wants to clean up when
        # a node is no longer connected

        return None

    def on_peer_disconnected(self, context):
        # TODO: possibly route messages to anyone who cares and wants to clean up when
        # a node is no longer connected
        msg, client = context
        if self.clients[msg.remote_ip + ":" + str(msg.remote_port)]:
            del self._connected_clients[msg.remote_ip + ":" + msg.remote_port]
        return None

    def on_peer_data_received(self, context):
        # TODO: buffer until a complete message is received then pass to
        # router.route(complete_message)
        return None

    def on_peer_data_sent(self, context):
        msg, client = context
        result = True #add this to the context and have Peer tell us if successful

        # TODO: Send a message to the person who requested data sent to let them know send was successful
        # e.g. if router.route( msg.callback ) where notify_completion_message is
        #      formed by the caller in the original message as an "event" notification
        if msg.success_callback and result:
            # could provide some info like msg.callback.property = value but prob unnecessary
            self.message_router.route(msg.success_callback)
        elif msg.failed_callback and not result:
            self.message_router.route(msg.failed_callback)

        client.stop()
        return None






