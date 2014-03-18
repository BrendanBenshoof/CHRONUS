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
import hash_util
from os import path
import json

DEFAULT_BLOCK_SIZE = 8192 # bytes

MAX_BLOCK_SIZE = float("inf")

backups = []

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




###END CLASSES###

###UTILITY FUNCTIONS###

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
        return list(iter(lambda: fin.read(DEFAULT_BLOCK_SIZE), ''))

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
    p = path.join(".","chunkStorage",str(chunkid)+".txt")
    return path.isfile(p)

def readChunk(chunkid):
    if iHaveChunk(chunkid):
        p = path.join(".","chunkStorage",str(chunkid)+".txt")
        raw = ""
        with file(p,"r") as fp:
            raw = fp.read()
        data = json.loads(raw)
        return Data_Atom(data,chunkid)

    else:
        raise Exception("Chunk is not locally stored")

def writeChunk(atom):
    p = path.join(".","chunkStorage",str(atom.hashkeyID)+".txt")
    with file(p,"wb") as fp:
        fp.write(json.dumps(atom.contents))

def makeKeyFile(name, chunkgen=locgicalBinaryChunk):
    k = KeyFile()
    k.name = name
    for a in chunkgen(name):
        ident = a.hashkeyID
        k.chunklist.append(ident)
        k.chunks[ident] = a
    return k

######SERVICE########


class CFS(Service):
    def __init__(self):
        super(CFS, self).__init__()
        self.service_id = "CFS"

    def handle_message(self, msg):
        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        #if not msg.service == self.service_id:
        #    raise "Mismatched service recipient for message."
        return msg.service == self.service_id

    def attach_to_console(self):
        ### return a dict of help texts, indexed by commands
        commands = {
            "storeFileRaw":"Stores the provided file with raw chunking",
            "storeFileLines":"Stores file with atomic lines",
            "storeFileWords":"Stores file with atomic words",
            "readFile":"dumps a bunch of json of a file stored on network",
            "readFromKeyfile":"reads a file from provided keyfile"
        }


        return commands

    def handle_command(self, comand_st, arg_str):
        ### one of your commands got typed in
        return None



    def change_in_responsibility(self,new_pred_key, my_key):
        pass #this is called when a new, closer predecessor is found and we need to re-allocate responsibilities



    # http://stackoverflow.com/questions/18761016/break-a-text-file-into-smaller-chunks-in-python

#####END SERVICE####
