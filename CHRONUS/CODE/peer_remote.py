from asyncoro import AsynCoroSocket, Coro, AsynCoro, Event, logger
import socket
import collections
from globals import *


class Peer_Remote():  # outbound connections
    def __init__(self, network_service, remote_ip, remote_port):
        self.exit = False
        self.network_service = network_service
        self.remote_ip = remote_ip
        self.remote_port = remote_port

        self.queue = collections.deque()
        self.signal_item_queued = Event()

        Coro(self._server_connect)

    def _server_connect(self, coro=None):
        pass  #logger.debug('CLIENT: connecting to peer at %s:%s', self.remote_ip, str(self.remote_port))
        self.outbound_socket = AsynCoroSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        yield self.outbound_socket.connect((self.remote_ip, self.remote_port))
        pass  #logger.debug('CLIENT: connected to peer at %s:%s', self.remote_ip, str(self.remote_port))
        Coro(self._client_send)
        Coro(self._client_recv)

    def _client_recv(self, coro=None):
        while True:
            data = yield self.outbound_socket.recv_msg()
            if not data:
                break
                #PYTHON DOES NOT HANDLE MULTILINE COMMANDS WELL. STOP

    def _client_send(self, coro=None):
        coro.set_daemon()
        while not self.exit:
            if not self.queue:
                self.signal_item_queued.clear()
                yield self.signal_item_queued.wait()
            cmd, state = self.queue.popleft()
            data, context = state
            if cmd == NETWORK_PEER_DISCONNECT:
                self.network_service.on_peer_disconnected(context)
                break

            
            pass  #logger.debug('CLIENT: sending data to %s:%s (Data is: %s)', self.remote_ip, self.remote_port,data)
            yield self.outbound_socket.send_msg(data)
            self.network_service.on_peer_data_sent(context) ##this used to br _sent(state). it is why nothing worked
        self.outbound_socket.shutdown(socket.SHUT_WR)


    def send(self, data, context):
        self.queue.append((None, (data, context)))
        self.signal_item_queued.set()

    def stop(self, context):
        self.exit = True
        pass  #logger.debug('CLIENT: disconnecting from %s:%s', self.remote_ip, str(self.remote_port))
        self.queue.append((NETWORK_PEER_DISCONNECT, context))
        self.signal_item_queued.set()



