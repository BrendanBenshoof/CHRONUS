from asyncoro import AsynCoroSocket, Coro, AsynCoro
import socket
import logging
import sys
from peer_zero_client import Peer_Zero_Client
from peer_zero_server import Peer_Zero_Server


class Peer_Zero():  # aka "The Deathstar - a fully functional battle station."
    def __init__(self,
                 host_ip="",  # listen on all interfaces
                 host_port=9999):
        self.host_ip = host_ip
        self.host_port = host_port

        self.server = Peer_Zero_Server(host_ip, host_port)

    def stop(self):
        self.server.stop()


# used for testing purposes
if __name__ == '__main__':
    # start peer zero
    pz = Peer_Zero("", 9999)
    cz = Peer_Zero_Client("127.0.0.1", 9999)
    cz.send("hello")
    cz.close()

    sys.stdin.readline()
    pz.quit( )

