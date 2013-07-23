from asyncoro import AsynCoroSocket, Coro, AsynCoro, Event, logger, AsynCoroThreadPool
import socket
import logging
import collections
import sys
import multiprocessing
from constants import *

# NOTE: If locks are needed you must use asyncoro Lock and for sleep asyncoro.sleep

class Peer_Local():  # inbound connections
    def __str__(self):
        return str(self.host_ip)+":"+str(self.host_port)

    exit = False
    def __init__(self, network_service,  # this architecture really should use message-based callbacks not interfaces
                 host_ip="", host_port=9999, context=None):
        self.exit = False
        self.network_service = network_service
        self.host_ip = host_ip
        self.host_port = host_port
        self.log_name = "SERVER(" + (self.host_ip if len(self.host_ip) > 0 else "127.0.0.1") + ":" + str(host_port) + "):"
        self.context = context

        if host_ip == "localhost" or host_ip == "127.0.0.1":
            host_ip = ""
        try:
            # start the server
            self.server_socket = AsynCoroSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1) # for now since we act like UDP
            self.server_socket.bind(("", host_port))
            self.server_socket.listen(128)  # set backlog to max

            # set logger flags in message_router
            logger.info(self.log_name + ' listening at %s', str(self.server_socket.getsockname()))

            self._server_coro = Coro(self.server_coro)

            # heuristic value (1 thread waiting plus 1 active at any given time)
            # remember to fix close() if more than one connection handler is started
            #for i in range(2 * multiprocessing.cpu_count()) :
            Coro(self._connection_handler)


            self.network_service.on_server_start(self,self.context, True)
        except:
            show_error()
            self.network_service.on_server_start(self, self.context, False)
    def _connection_handler(self, coro=None):
        coro.set_daemon()

        #for performance reasons we may need to put this in a thread pool (multiple outstanding accepts)
        while not self.exit:
            try:
                logger.debug(self.log_name + "outstanding accept( )")
                client_socket, client_addr = yield self.server_socket.accept()
                if self.exit:
                    break

                Coro(self.client_coro, client_socket, client_addr)
            except:
                show_error()
        print self.log_name + "Coro(_connection_handler) exiting"

    def stop(self, context=None):
        self.exit = True

        # fastest clean exit from yield accept() is to connect to ourselves
        # loop if multiple outstanding accepts
        try:
            #for i in range(2 * multiprocessing.cpu_count()) :
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.host_ip if len(self.host_ip) > 0 else "127.0.0.1", self.host_port))
                s.close()
        except:
            show_error()

        self._server_coro.send((None,None))

    def server_coro(self, coro=None):
        coro.set_daemon()
        clients = set()
        while not self.exit:
            try:
                cmd, item = yield coro.receive()
                if self.exit:
                    break

                if cmd == NETWORK_PEER_CONNECTED:
                    client_socket, client_addr = item
                    logger.debug(self.log_name + str(self) + ': client %s connected', str(client_addr))
                    self.network_service.on_peer_connected(item)
                    clients.add((client_socket, client_addr))
                elif cmd == NETWORK_PEER_DISCONNECTED:
                    try:
                        client_socket, client_addr = item
                        logger.debug(self.log_name + str(self) + ': client %s disconnected', str(client_addr))
                        self.network_service.on_peer_disconnected(item)
                    finally:
                        clients.discard((client_socket, client_addr))
                        client_socket.close()
                elif cmd == NETWORK_PEER_DATA_RECEIVED:
                    try:
                        client_socket, client_addr, data = item
                        #logger.debug('SERVER ' + str(self) + ': Data received from %s (Data: %s)', str(client_addr), data)
                        self.network_service.on_peer_data_received((self,client_addr,data))
                    except:
                        show_error()
                elif cmd == NETWORK_PEER_DATA_SENT:
                    client_socket, client_addr, data = item
                    #logger.debug('SERVER ' + str(self) + ': Data sent to %s (Data: %s)', str(client_addr), data)
                    self.network_service.on_peer_data_sent(data)
                elif cmd == NETWORK_TERMINATE:
                    self.network_service.on_server_stop(item)
                    break
            except:
                show_error()

        #self.server_socket.shutdown(socket.SHUT_RDWR)
        #self.server_socket.close()
        print self.log_name + "Coro(server_coro) exiting"


    # handle communication from the client
    def client_coro(self, client_socket, client_addr, coro=None):

        self._server_coro.send((NETWORK_PEER_CONNECTED, (client_socket, client_addr)))
        while True:
            try:
                data = yield client_socket.recv_msg()
                if not data:
                    self._server_coro.send((NETWORK_PEER_DISCONNECTED, (client_socket, client_addr)))
                    break
                else:
                    self._server_coro.send((NETWORK_PEER_DATA_RECEIVED, (client_socket, client_addr, data)))
                    #break # for now we expect to act more like UDP
            except:
                show_error()
        #print "Coro(client_coro) exiting"


