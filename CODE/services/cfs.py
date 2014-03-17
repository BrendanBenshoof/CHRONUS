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

maintain ownership of files????
We can implement so kind of public/private key owership later on


when do files expire? (never, but in general?)?
In the ideal setup, files are given a time at creation.  they expire at this specified time (or after specified time passes) unless they are renewed.  
If they are provided with a time of 0, they don't expire



Can we just extend one of the database services?
"""
from service import *
from message import *
from hash_util import *
import Queue
import node
from threading import Thread
import time
import importlib



BLOCK_SIZE = 8192 # bytes
backups = []



class CFS(Service):
    def __init__(self):
        super(CFS, self).__init__()
        self.service_id = "CFS"

        
        
    
    # http://stackoverflow.com/questions/18761016/break-a-text-file-into-smaller-chunks-in-python
    def chunk(fname):
        with open(fname, 'rb') as fin:
            return list(iter(lambda: fin.read(BLOCK_SIZE), ''))          
