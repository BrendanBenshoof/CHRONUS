#webserver
import BaseHTTPServer
import Queue
import cgi
import threading
import json

def convert(i):#de-unicodes json
    if isinstance(i, dict):
        return {convert(key): convert(value) for key, value in i.iteritems()}
    elif isinstance(i, list):
        return [convert(element) for element in i]
    elif isinstance(i, unicode):
        return i.encode('utf-8')
    else:
        return i

def pack(stuff):
    return json.dumps(stuff,separators=(',',':'))

def unpack(string):
    return convert(json.loads(string))



outQueue = Queue.Queue()
contents = {"*":"test"}

class MasterHand(object,BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self,request, client_address, server):
        global outQueue, contents
        self.contents = contents
        self.output = outQueue
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self,request,client_address,server)


    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()

    def do_GET(self):
        id = self.path[1:]
        output= []
        if "*" in self.contents.keys():
            output.append(self.contents["*"])
        if id in self.contents.keys():
            output.append(self.contents[id])
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.wfile.write(pack(output))

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        instr = self.rfile.read(length)
        self.output.put(instr)
        self.send_response(200)
        self.end_headers()
        self.send_header("Content-type", "text/json")
        self.wfile.write(self.contents)
        print "done"

def getQueue():
    global outQueue
    return outQueue

def getContents():
    global contents
    return contents

def setContents(s):
    global contents
    contents = s
    return contents

def start():
    server = ('',9080)
    httpd = BaseHTTPServer.HTTPServer(server,MasterHand)
    httpdThread = threading.Thread(target=httpd.serve_forever)
    httpdThread.start()


