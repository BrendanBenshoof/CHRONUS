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
        logger.debug('CLIENT: connecting to peer at %s:%s', self.remote_ip, str(self.remote_port))
        self.outbound_socket = AsynCoroSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        yield self.outbound_socket.connect((self.remote_ip, self.remote_port))
        logger.debug('CLIENT: connected to peer at %s:%s', self.remote_ip, str(self.remote_port))
        Coro(self._client_send)
        Coro(self._client_recv)

    def _client_recv(self, coro=None):
        while True:
            data = yield self.outbound_socket.recv_msg()
            if not data:
                break
            logger.debug('CLIENT: received data to peer at %s:%s (Data: %s)',
                         self.remote_ip, str(self.remote_port), data)
            self.network_service.on_peer_data_received(data)

    def _client_send(self, coro=None):
        coro.set_daemon()
        while not self.exit:
            if not self.queue:
                self.signal_item_queued.clear()
                yield self.signal_item_queued.wait()
            cmd, state = self.queue.popleft()
            if cmd == NETWORK_PEER_DISCONNECT:
                self.network_service.on_peer_disconnected(state)
                break

            data, context = state
            logger.debug('CLIENT: sending data to %s:%s (Data is: %s)', self.remote_ip, self.remote_port,data)
            yield self.outbound_socket.send_msg(data)
            self.network_service.on_peer_data_sent(state)
        self.outbound_socket.shutdown(socket.SHUT_WR)


    def send(self, data, context):
        self.queue.append((None, (data, context)))
        self.signal_item_queued.set()

    def stop(self, context):
        self.exit = True
        logger.debug('CLIENT: disconnecting from %s:%s', self.remote_ip, str(self.remote_port))
        self.queue.append((NETWORK_PEER_DISCONNECT, context))
        self.signal_item_queued.set()



