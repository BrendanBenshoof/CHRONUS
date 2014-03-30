#Chord File System

"""
TODO:

write File
    binary files
    folders/archives?
    manual or automatic chunking? both?
    
    Let's KISS
    For the experiment we're splitting up text.  Let's not make it anymore complicated that that
    Split the the file into 8kB chunks and spread it around the network
    

read File
    assemble recursively?
    merge to binary file?
    merge to tree of chunks?
    
    Good questions.  I was just assuming that if the file was split into k blocks, the seeker sent out k messages.
    The seeker was the one responsible for assembling them.

backup files
    -backup scheme?
    
    They should follow the exact same scheme as regular files.

utility functions:
    get keyfile from name
    get chunks from keyfile
    do I own/have a particular chunk locally?
    get all local chunks from a list
    new implementation of the smart forwarding scheme (we only need to recurse if the message range still contains a file chunk)



maintain ownership of files????
We can implement so kind of public/private key owership later on


when do files expire? (never, but in general?)?
In the ideal setup, files are given a time at creation.  they expire at this specified time (or after specified time passes) unless they are renewed.  
If they are provided with a time of 0, they don't expire



Can we just extend one of the database services?
"""
from service import Service
from message import Message

import node
import hash_util

from os import path
import json
from Queue import Queue
import time


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


SERVICE_CFS = "CFS"

DEFAULT_BLOCK_SIZE = 1024*8 # bytes

MAX_BLOCK_SIZE = float("inf")

backups = []

singleton = None
def getCFSsingleton():
    global singleton
    if not singleton:
        singleton = CFS()
    return singleton


###UTILITY CLASES###
class Data_Atom(object):
    def __init__(self,contents,hashkeyID=None):
        #assumes contents are objects not jsonDUMPs
        if hashkeyID is None:
            self.hashkeyID = hash_util.hash_str(str(contents))
        else:
           self.hashkeyID = hashkeyID
        self.contents = contents
        #print hashkeyID

    def __str__(self):
        return str(self.contents)


class KeyFile(object):
    def __init__(self):
        self.name = ""
        self.chunklist = [] #list of identfiers
        self.chunks = {} #dict of id:data_atom
    def __str__(self):
        chunklistStrings = map(str,self.chunklist)
        summary = {"name":self.name,"chunklist":chunklistStrings}
        return pack(summary)

    @classmethod
    def parse(cls,string):
        summary = unpack(string)
        k = cls()
        k.name = summary["name"]
        k.chunklist = map(hash_util.Key, summary["chunklist"])
        return k


class OpenRequest(object):
    def __init__(self, chunkid):
        self.outqueue = Queue(1)
        self.chunkid = chunkid


###END CLASSES###

###UTILITY FUNCTIONS###

def disribute_fairly(atoms):
    distribution = {}
    for a in atoms:
        if node.I_own_hash(a.hashkeyID):
            dest = node.thisNode
        else:
            dest = node.find_ideal_forward(a.hashkeyID)
        try:
            distribution[dest].append(a)
        except KeyError:
            distribution[dest] = [a]
    return distribution


def asciifilter(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])

def lineChunk(fname):
    with open(fname, 'rb') as fin:
        return list(iter(fin.readline,''))

def wordChunk(fname):
    raw_text = ""
    with open(fname, 'rb') as fin:
        raw_text = fin.read()
    return raw_text.split()

def binaryChunk(fname):
    with open(fname, 'rb') as fin:
        return list(iter(lambda: asciifilter(fin.read(DEFAULT_BLOCK_SIZE)), ''))

def binaryChunkPack(chunkIterator,maxsize=DEFAULT_BLOCK_SIZE):
    #assumes you are using strings
    #if a single chunk is bigger than maxsize, it sends it anyway
    current_chunk = ""
    for c in chunkIterator:
        if len(current_chunk) + len(c)+1 <= maxsize:
            current_chunk+=" "+c
        else:
            yield current_chunk
            current_chunk = c
    if current_chunk:#empty string is falsey
        yield current_chunk

def logicalChunk(chunkIterator):
    return map(lambda c: Data_Atom(c,None), chunkIterator)

def locgicalBinaryChunk(filename):
    return logicalChunk(binaryChunk(filename))

###END UTILITY FUNCTIONS###

###LOCAL FILE FUNCTIONS###

def iHaveChunk(chunkid):
    p = path.join(".","chunkStorage",str(chunkid)+".chunk")
    return path.isfile(p)

def readChunk(chunkid):
    if iHaveChunk(chunkid):
        p = path.join(".","chunkStorage",str(chunkid)+".chunk")
        raw = ""
        with file(p,"r") as fp:
            raw = fp.read()
        data = unpack(raw)
        return Data_Atom(data,chunkid)

    else:
        raise Exception("Chunk is not locally stored")

def writeChunk(atom):
    p = path.join(".","chunkStorage",str(atom.hashkeyID)+".chunk")
    with file(p,"w") as fp:
        fp.write(pack(atom.contents))

def makeKeyFile(name, chunkgen=locgicalBinaryChunk):
    k = KeyFile()
    k.name = name
    for a in chunkgen(name):
        ident = a.hashkeyID
        k.chunklist.append(ident)
        k.chunks[ident] = a
    return k




######Messages######

class CFS_Message(Message):
    #valid actions: GET, PUT, RESP
    def __init__(self, origin_node, destination_key, Response_service=SERVICE_CFS, action="GET"):
        Message.__init__(self, SERVICE_CFS, action)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.add_content("service",Response_service)
        self.reply_to = origin_node



######SERVICE########


class CFS(Service):
    def __init__(self):
        super(CFS, self).__init__()
        self.service_id = "CFS"
        self.open_requests = {}


    def handle_message(self, msg):
        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        if msg.type == "GET":
            chunkid = msg.destination_key
            data = None

            if iHaveChunk(chunkid):
                data = readChunk(chunkid)

            m = CFS_Message(self.owner, msg.reply_to.key, Response_service=SERVICE_CFS, action="RESP")
            m.add_content("chunkid",chunkid)
            m.add_content("data",data)
            self.send_message(m,msg.reply_to)

        elif msg.type == "PUT":
            content = msg.get_content("data")
            writeChunk(content)

        elif msg.type == "RESP":
            chunkid = msg.get_content("chunkid")
            
            if chunkid in self.open_requests:
                content = msg.get_content("data")
                self.open_requests[chunkid].outqueue.put(content)
        elif msg.type == "BULK":
            atoms = msg.get_content("bulk")
            mystuff = self.polite_distribute(atoms)
            for a in mystuff:
                writeChunk(a)
        else:
            pass





    def attach_to_console(self):
        ### return a dict of help texts, indexed by commands
        commands = {
            "storeFileRaw":"Stores the provided file with raw chunking",
            "storeFileLines":"Stores file with atomic lines",
            "storeFileWords":"Stores file with atomic words",
            "readFileRaw":"writes a raw file from provided key file",
            "readFile":"writes a json dump of chunks from provided key file",
            "get":"Reads a single chunk off the network",
            "put":"Writes a single chunk to the network"
        }


        return commands

    def handle_command(self, comand_st, arg_str):
        ### one of your commands got typed in
        return None



    def change_in_responsibility(self,new_pred_key, my_key):
        pass #this is called when a new, closer predecessor is found and we need to re-allocate responsibilities

    def getChunk(self,chunkid,timeout=-1):
        m = CFS_Message(self.owner, chunkid, Response_service=SERVICE_CFS, action="GET")
        request = OpenRequest(chunkid)
        self.open_requests[chunkid] = request
        self.send_message(m,None)
        output = None
        try:
            if timeout > 0:
                output = request.outqueue.get(True,timeout)
            else:
                output = request.outqueue.get(True,None)
        finally:
            del self.open_requests[chunkid]
            return output

    def putChunk(self,atom):
        chunkid = atom.hashkeyID
        m = CFS_Message(self.owner, chunkid, Response_service=SERVICE_CFS, action="PUT")
        m.add_content("data",atom)
        self.send_message(m,None)

    def writeFile(self,key):
        keyfilestr = str(key)
        hashid = hash_util.hash_str(key.name)
        d = Data_Atom(keyfilestr,hashid)
        self.putChunk(d)
        atoms = []
        for k in key.chunks:
            atoms.append(key.chunks[k])
        mystuff = self.polite_distribute(atoms)
        for a in mystuff:
            writeChunk(a)

    def polite_distribute(self, atoms):
        forward_dests = disribute_fairly(atoms)
        mystuff = []
        if self.owner in forward_dests.keys():
            mystuff = forward_dests[self.owner][:]
            try:
                del forward_dests[self.owner]
            except KeyError:
                pass
        atoms_sent = 0
        atoms_total = len(atoms)-len(mystuff)
        for k in forward_dests.keys():
            if len(forward_dests[k]) > 0:
                datatoms = forward_dests[k]
                m = CFS_Message(self.owner, k.key, Response_service=SERVICE_CFS, action="BULK")
                m.add_content("bulk",datatoms)
                self.send_message(m,k)
        return mystuff


    

#####END SERVICE####
