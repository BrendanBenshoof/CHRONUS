#simpler networking solution
import SocketServer
import threading
import socket
import node
import message



class NETWORK_SERVICE(object):
    def send_message(self,msg,dest):
        msg_function = lambda: client_send(dest,msg)
        t = threading.Thread(target=msg_function)
        t.daemon = True
        t.start()

    def __init__(self,HOST="localhost",PORT=9000):
        # Create the server, binding to localhost on port 9999
        self.server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        t = threading.Thread(target=self.server.serve_forever)
        t.daemon = True
        t.start()

def client_send(dest, msg):
    HOST = dest.IPAddr
    PORT = dest.ctrlPort
    DATA = msg.serialize()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to server and send data
        sock.settimeout(3.0)
        sock.connect((HOST, PORT))
        sock.sendall(DATA + "DONEDONE")

        # Receive data from the server and shut down
    except IOError as inst: 
        sock.close()
        node.message_failed(msg,dest)
    finally:
        sock.close()
        return True


class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def __init__(self, request, client_address, server):
        self.data = ""
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)



    def handle(self):
        # self.request is the TCP socket connected to the client
        DONE = False
        while not DONE:
            self.data+=self.request.recv(1024)
            if len(self.data)>=8:
                if self.data[-8:]=="DONEDONE":
                    DONE = True
            #print self.data
        # just send back the same data, but upper-cased
        self.data = self.data[0:-8]
        self.request.sendall("ACK")
        msg = message.Message.deserialize(self.data)
        node.handle_message(msg)