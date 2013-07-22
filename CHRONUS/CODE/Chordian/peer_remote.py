from asyncoro import AsynCoroSocket, Coro, AsynCoro, Event, logger
import socket
import collections
import logging
from constants import *
import sys

class Peer_Remote():  # outbound connections
    def __init__(self, network_service, remote_ip, remote_port, context=None):
        self.exit = False
        self.network_service = network_service
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.context = context

        Coro(self._server_connect)

    def _server_connect(self, coro=None):
        try:
            logger.debug('CLIENT: connecting to peer at %s:%s', self.remote_ip, str(self.remote_port))
            self.outbound_socket = AsynCoroSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            self.outbound_socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1) # if you're gonna act like UDP

            yield self.outbound_socket.connect((self.remote_ip, self.remote_port))
            logger.debug('CLIENT: connected to peer at %s:%s', self.remote_ip, str(self.remote_port))
            self._send_coro = Coro(self._client_send)
            #Coro(self._client_recv) # unneeded if we don't utilize bi-directional communication in UDP style messaging

            self.network_service.on_server_connect(self, self.context)
        except:
            show_error()
            raise

    def _client_recv(self, coro=None):
        while not self.exit:
            try:
                data = yield self.outbound_socket.recv_msg()
                if data == None or len(data) == 0:
                    break
                #logger.debug('CLIENT: received data to peer at %s:%s (Data: %s)', self.remote_ip, str(self.remote_port), data)
                self.network_service.on_peer_data_received(data)
            except:
                show_error()
                #break
        #print "Coro(_client_recv) exiting"

    def _client_send(self, coro=None):
        coro.set_daemon()
        while True:
            try:
                cmd, state = yield self._send_coro.receive()
                data, context = state
                if cmd == NETWORK_PEER_DISCONNECT:
                    self.network_service.on_client_disconnected(context)
                    break

                #logger.debug('CLIENT: sending data to %s:%s (Data is: %s)', self.remote_ip, self.remote_port,data)
                yield self.outbound_socket.send_msg(data)
                self.network_service.on_client_data_sent(context)
            except:
                show_error()
                #break

        self.outbound_socket.shutdown(socket.SHUT_RDWR)
        self.outbound_socket.close()
        #print "Coro(_client_send) exiting"


    def send(self, data, context):
        self._send_coro.send((None, (data, context)))

    def stop(self, context=None):
        self.exit = True
        logger.debug('CLIENT: disconnecting from %s:%s', self.remote_ip, str(self.remote_port))
        self._send_coro.send((NETWORK_PEER_DISCONNECT, (None,context)))



