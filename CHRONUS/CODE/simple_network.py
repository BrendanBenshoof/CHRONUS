#simpler networking solution
import SocketServer
import threading
import socket
import node
import message
import Queue
import time



class NETWORK_SERVICE(object):
    def sender_loop(self):
            while True:
                try:
                    dest, msg = self.tosend.get(True,0.1)
                    client_send(dest,msg)
                    self.tosend.task_done()
                    print "*",
                except Queue.Empty:
                    time.sleep(0.1)

    def send_message(self,msg,dest):
        msg_pack = (dest,msg)
        self.tosend.put(msg_pack,True)
        

    def __init__(self,HOST="localhost",PORT=9000):
        # Create the server, binding to localhost on port 9999
        self.server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
        self.tosend = Queue.Queue()
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        t = threading.Thread(target=self.server.serve_forever)
        t.daemon = True
        t.start()
        for i in range(0,2):
            t2 = t = threading.Thread(target=self.sender_loop)
            t2.daemon = True
            t2.start()

    def stop(self):
        self.server.shutdown()

def client_send(dest, msg):
    ##print "hello world"
    HOST = dest.IPAddr
    PORT = dest.ctrlPort
    DATA = msg.serialize()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    length = len(DATA)
    padding = 8-length%8
    DATA+=" "*padding
    length = len(DATA)/8
    byte1 = length >> 8
    byte2 = length % (2**8)
    ##print byte1, byte2
    b1 = chr(byte1)
    b2 = chr(byte2)
    ##print b1, b2, ord(b1), ord(b2)
    try:
        # Connect to server and send data
        sock.settimeout(3.0) 
        sock.connect((HOST, PORT))
        sock.send(b1)
        sock.send(b2)
        ack = ""
        while len(ack)==0:
            ack = sock.recv(1)
        sock.send(DATA)
        sock.shutdown(socket.SHUT_WR)
        # Receive data from the server and shut down
        self.request.recv(1024)
    except socket.timeout as e:
        #print e
        sock.close()
        node.message_failed(msg,dest)
    finally:
        sock.close()
        #print DATA[-20:],len(DATA)%8
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
        b1 = ""
        b2 = ""
        while len(b1) == 0:
            b1 = self.request.recv(1)
        while len(b2) == 0:
            b2 = self.request.recv(1)
        ##print b1, b2
        b1 = ord(b1)
        b2 = ord(b2)
        length = ((b1 << 8) + b2)*8
        ##print length
        self.request.send("0")
        data = ""
        while length > 0:
            ##print length
            data += self.request.recv(length)
            length-=len(data)
        data = data.rstrip()
        #print "incoming length: " +str(len(data))
        #print "I GOT:", data[-20:]
        msg = message.Message.deserialize(data)
        node.handle_message(msg)
