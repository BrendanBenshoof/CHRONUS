import Queue
import time

from shelver_service import *
from super_service import Service
import hash_util
from constants import *


class Partial_file(object):
    def __init__(self,filename):
        self.filename = filename
        self.filehash_name = hash_util.hash_str(filename)
        self.done = False
        self.has_key = False
        self.input_stream = Queue.Queue()
        self.chunklist = []
        self.chunks = {}
    
    def add_key(self,keyfile):
        lines = keyfile.split("\n")
        if lines[0]!="KEYFILE":
            return False
        if lines[1]!=self.filename:
            return False
        for l in lines[2:]:
            self.chunklist.append(l)
        self.hash_key = True

    def process_queue(self):
        while not self.input_stream.empty():
            next_msg = self.input_stream.get(True,0.1)
            chunkid = str(next_msg.destination_key)
            addr, cont = next_msg.file_contents.split("\n",1)
            self.chunks[chunkid] = cont
            self.input_stream.task_done()
        done = True
        for c in self.chunklist:
            if not c in self.chunks.keys():
                done = False
        self.done = done
        return done

    def get_file(self,blocking=False):
        if self.done:
            output = ""
            for c in self.chunklist:
                output+=self.chunks[c]
            return output
        elif blocking:
            while not self.done:
                time.sleep(0.1)
            output = ""
            for c in self.chunklist:
                output+=self.chunks[c]
            return output
        else:
            return None
                

class File_Service(Service):
    """This object is intented to act as a parent/promise for Service Objects"""
    def __init__(self, message_router):
        super(File_Service, self).__init__(SERVICE_FILE, message_router)
        self.partial_files = {}

    def read(self,node_info, filename):
        sw = Stopwatch()
        filehash = hash_util.hash_str(filename)
        new_partial = Partial_file(filename)
        self.partial_files[str(filehash)]=new_partial
        get_keyfile_message = Message_Forward(node_info, filehash, Database_Get_Message(node_info,filehash))
        self.send_message(get_keyfile_message,None)
        sw.elapsed("read")

    def store(self, node_info, filename, segment_size=128):
        sw = Stopwatch()
        segment_ids = []
        segments = []
        with open(filename, "rb") as f:
            byte = f.read(segment_size)
            while byte:
                newid = hash_util.generate_random_key().key
                segment_ids.append(newid)
                segments.append(byte)
                byte = f.read(segment_size)
        keyfile = "KEYFILE\n"+filename+"\n"+reduce(lambda x,y: x+"\n"+y,segment_ids)
        keyfile_hash = hash_util.hash_str(filename)
        keyfile_message = Message_Forward(node_info,keyfile_hash,Database_Put_Message(node_info, keyfile_hash, keyfile))
        self.send_message(keyfile_message,None)
        number_of_chunks = len(segments)
        for i in range(0,number_of_chunks):
            actual_contents = str(keyfile_hash)+"\n"+segments[i]
            seg_hash = hash_util.Key(segment_ids[i])
            chunkfile_message = Message_Forward(node_info,seg_hash,Database_Put_Message(node_info,seg_hash, actual_contents))
            self.send_message(chunkfile_message,None)

        print filename + " has been persisted to (" + str(node_info) + ")"
        sw.elapsed("store")

    def handle_message(self, msg):
        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        if not msg.dest_service == self.service_id:
            raise Exception("Mismatched service recipient for message.")
        elif msg.type == Database_Get_Message_Response.Type():
            contents = msg.file_contents
            fileid = msg.destination_key
            if contents[:7] == "KEYFILE":
                partial = self.partial_files[str(fileid)]
                partial.add_key(contents)
                for k in partial.chunklist:
                    get_datafile_message = Database_Get_Message(msg.origin_node, hash_util.Key(k))
                    self.send_message(get_datafile_message,None)
            elif contents == "404 Error":
                print contents
            else:
                #print contents
                addr, cont = contents.split("\n",1)
                if addr in self.partial_files.keys():
                    self.partial_files[addr].input_stream.put(msg)
                    if self.partial_files[addr].process_queue():
                        print "FINISHED FILE"
                        print self.partial_files[addr].get_file(True)
        elif msg.type == Message_Console_Command.Type():
            self.handle_command(msg)

    def attach_to_console(self):
        ### return a list of command-strings
        return ["store","read"]

    def handle_command(self, msg):
        if msg.command == "store" and len(msg.args) == 1:
            self.store(msg.console_node, msg.args[0])
        elif msg.command == "read" and len(msg.args) == 1:
            self.read(msg.console_node, msg.args[0])

    def send_message(self, msg, destination=None):
        self.message_router.route(msg)
