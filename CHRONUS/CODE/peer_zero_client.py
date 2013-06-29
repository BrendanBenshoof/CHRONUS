from asyncoro import AsynCoroSocket, Coro, AsynCoro, Event, logger
import socket
import collections
from peer_zero_signal import Peer_Zero_Signal


class Peer_Zero_Client():  # outbound connections
    def __init__(self, message_handler, client_ip, client_port):
        self.exit = False
        self.message_handler = message_handler
        self.client_ip = client_ip
        self.client_port = client_port

        self.queue = collections.deque()
        self.signal_item_queued = Event()

        Coro(self._server_connect)

    def _server_connect(self, coro=None):
        logger.debug('CLIENT: connecting to peer at %s:%s', self.client_ip, str(self.client_port))
        self.outbound_socket = AsynCoroSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        yield self.outbound_socket.connect((self.client_ip, self.client_port))
        logger.debug('CLIENT: connected to peer at %s:%s', self.client_ip, str(self.client_port))
        Coro(self._client_send)
        Coro(self._client_recv)

    def _client_recv(self, coro=None):
        while True:
            line = yield self.outbound_socket.recv_msg()
            if not line:
                break
            print(line)

    def _client_send(self, coro=None):
        coro.set_daemon()
        while not self.exit:
            if not self.queue:
                self.signal_item_queued.clear()
                yield self.signal_item_queued.wait()
            cmd, data = self.queue.popleft()
            if cmd == Peer_Zero_Signal.DISCONNECT():
                break

            logger.debug('CLIENT: sending data to %s:%s (Data is: %s)', self.client_ip, self.client_port, data)
            yield self.outbound_socket.send_msg(data)
        self.outbound_socket.shutdown(socket.SHUT_WR)


    def send(self, data):
        self.queue.append((None, data))
        self.signal_item_queued.set()

    def close(self):
        self.exit = True
        logger.debug('CLIENT: disconnecting from %s:%s', self.client_ip, str(self.client_port))
        self.queue.append((Peer_Zero_Signal.DISCONNECT(), None))
        self.signal_item_queued.set()



