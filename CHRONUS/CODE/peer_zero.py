from asyncoro import AsynCoroSocket, Coro, AsynCoro
import socket
import logging
import sys
from peer_zero_client import Peer_Zero_Client
from peer_zero_server import Peer_Zero_Server

class Peer_Zero():  # aka "The Deathstar - a fully functional battle station."

    def __init__(self,
                 message_handler,
                 host_ip="",  # listen on all interfaces
                 host_port=9999):
        self.message_handler = message_handler
        self.host_ip = host_ip
        self.host_port = host_port

        self.server = Peer_Zero_Server(message_handler, host_ip, host_port)

    def quit(self):
        self.server.quit()


# used for testing purposes
if __name__ == '__main__':
    # start peer zero
    pz = Peer_Zero(None, "", 9999)
    cz = Peer_Zero_Client(None, "127.0.0.1", 9999)
    cz.send("hello")
    cz.close()

    sys.stdin.readline()

