from super_service import Service
from service_message import *
from peer_local import Peer_Local
from peer_remote import Peer_Remote

class Network_Service(Service):
    """Interface to the outside world"""
    def __init__(self, message_router):
        super(Network_Service, self).__init__(SERVICE_NETWORK, message_router, cl_name="ns")

        self.clients = {}
        self.servers = {}

    def handle_message(self, msg):
        if not msg.dest_service == self.service_id:
            raise Exception("Mismatched service recipient for message.")

        if msg.type == Message_Start_Server.Type():
            try:
                server = Peer_Local(self, msg.host_ip, msg.host_port)
                self.servers[msg.host_ip + ":" + str(msg.host_port)] = server
                self.on_server_start((msg, server, True))
            except:
                self.on_server_start((msg, server, False))
                raise
        elif msg.type == Message_Stop_Server.Type():
            server = self.servers[msg.local_ip + ":" + str(msg.local_port)]
            server.stop((msg, server))
        elif msg.type == Message_Send_Peer_Data.Type():
            client = Peer_Remote(self, msg.remote_ip, msg.remote_port)
            self.clients[msg.remote_ip + ":" + str(msg.remote_port)] = client
            client.send(msg.raw_data, (msg,client))
#        elif msg.type == MESSAGE_DISCONNECT_PEER:
#            client = self.clients[msg.remote_ip + ":" + str(msg.remote_port)]
#            if client:
#                client.stop((msg, client))

    def on_server_start(self, context):
        msg, server, result = context
        if msg.success_callback_msg and result:
            self.message_router.route(msg.success_callback_msg)
        elif msg.failed_callback_msg and result:
            self.message_router.route(msg.failed_callback_msg)

    def on_server_stop(self, context):
        # TODO: possibly route messages to anyone who cares and wants to clean up when
        # the server has shut down
        msg, server = context
        try:
            if self.servers.has_key(msg.host_ip + ":" + str(msg.host_port)):
                del self.servers[msg.host_ip + ":" + str(msg.host_port)]
        except KeyError:
            pass
        return None

    def on_peer_connected(self, context):
        # TODO: possibly route messages to anyone who cares and wants to clean up when
        # a node is no longer connected

        pass

    def on_peer_disconnected(self, context):
        # TODO: possibly route messages to anyone who cares and wants to clean up when
        # a node is no longer connected

        pass

    def on_peer_data_received(self, context):
        server, client, data = context
        msg = Message.deserialize(data)
        if msg:
            self.message_router.route(Message_Recv_Peer_Data(server.host_ip, server.host_port, data))

    def on_client_disconnected(self, context):
        # TODO: possibly route messages to anyone who cares and wants to clean up when
        # a node is no longer connected
        msg, client = context
        if self.clients.has_key(client.remote_ip + ":" + str(client.remote_port)):
            del self.clients[client.remote_ip + ":" + str(client.remote_port)]

    def on_client_data_sent(self, context):
        msg, client = context
        result = True

        # TODO: Send a message to the person who requested data sent to let them know send was successful
        # e.g. if router.route( msg.callback ) where notify_completion_message is
        #      formed by the caller in the original message as an "event" notification
        if msg.success_callback_msg and result:
            # could provide some info like msg.callback.property = value but prob unnecessary
            self.message_router.route(msg.success_callback_msg)
        elif msg.failed_callback_msg and not result:
            self.message_router.route(msg.failed_callback_msg)

        client.stop(context)


