from asyncoro import AsynCoroSocket, Coro, AsynCoro, Event, logger, AsynCoroThreadPool
import socket
import logging
import collections
import sys
import multiprocessing
from peer_zero_signal import Peer_Zero_Signal


class Peer_Zero_Server():  # inbound connections

    def __init__(self, message_handler, host_ip="",host_port=9999):
        self.exit = False

        # start the server
        logger.setLevel(logging.DEBUG)
        self.server_socket = AsynCoroSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host_ip, host_port))
        self.server_socket.listen(128)  # set backlog to max
        logger.info('SERVER: listening at %s', str(self.server_socket.getsockname()))

        self.queue = collections.deque()
        self.signal_item_queued = Event()
        self.signal_item_queued.clear()

        Coro(self.server_coro)

        # heuristic value (1 thread waiting plus 1 active at any given time)
        for i in range(2 * multiprocessing.cpu_count()) :
            Coro(self._connection_handler)

    def _connection_handler(self, coro=None):
        coro.set_daemon()

        #for performance reasons we may need to put this in a thread pool (multiple outstanding accepts)
        while not self.exit:
            try:
                logger.debug("SERVER: outstanding accept( )")
                client_socket, client_addr = yield self.server_socket.accept()
                Coro(self.client_coro, client_socket, client_addr)
            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise

    def close(self):
        self.exit = True
        self.queue.append(('terminate', None))
        self.signal_item_queued.set()

        # poor man's exit (graceful exit would allow all open connections to unwind & threads to exit normally)
        # for the graceful exit we would shutdown the listening socket and possibly issue connections
        # to localhost to cause outstanding "accept" calls to return or make "accept" calls timeout
        self.server_socket.close()

    def server_coro(self, coro=None):
        coro.set_daemon()
        clients = set()
        while True:
            if not self.queue:
                self.signal_item_queued.clear()
                yield self.signal_item_queued.wait()

            cmd, item = self.queue.popleft()
            if cmd == Peer_Zero_Signal.CONNECT():
                client_socket, client_addr = item
                logger.debug('SERVER: %s connected', str(client_addr))
                clients.add((client_socket, client_addr))
            elif cmd == Peer_Zero_Signal.DISCONNECT():
                client_socket, client_addr = item
                clients.discard((client_socket, client_addr))
                logger.debug('SERVER: %s disconnected', str(client_addr))
                client_socket.close()
            elif cmd == Peer_Zero_Signal.TERMINATE():
                break

    # handle communication with the client
    def client_coro(self, client_socket, client_addr, coro=None):

        self.queue.append((Peer_Zero_Signal.CONNECT(), (client_socket, client_addr)))
        self.signal_item_queued.set()

        while True:
            data = yield client_socket.recv_msg()
            if not data:
                self.queue.append((Peer_Zero_Signal.DISCONNECT(), (client_socket, client_addr)))
                self.signal_item_queued.set()
                break
            else:
                logger.debug('SERVER: Data received from %s (Data: %s)', str(client_addr), data)
                #self.queue.append((Peer_Zero_Signal.DISCONNECT(), (client_socket, client_addr)))
                #self.signal_item_queued.set()

