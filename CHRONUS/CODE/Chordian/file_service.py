import Queue
import time

from shelver_service import *
from super_service import Service
import hash_util
from constants import *
from asyncoro import AsynCoro, Coro, AsynCoroThreadPool, logger
import multiprocessing
import collections

class Partial_file(object):
    def __init__(self,filename):
        self.sw = Stopwatch()
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
            # if you need to block then set this up with an event rather than a context-swapping
            # spin wait
            #while not self.done:
            #    time.sleep(0.1)
            output = ""
            for c in self.chunklist:
                output+=self.chunks[c]
            return output
        else:
            return None

class Upload_File_Task(object):
    def __init__(self,node_info,filename, segment_size=128):
        self.sw_total = Stopwatch()
        self.segment_ids = []
        self._confirmed = 0
        self.messages = collections.deque()
        self.node_info = node_info
        self.segment_size = segment_size
        self.filename = filename

    def process_file(self):
        try:
            self.sw_reading = Stopwatch()
            keyfile_hash = hash_util.hash_str(self.filename)
            with open(self.filename, "rb") as f:
                try:
                    bytes = f.read(self.segment_size)
                    while bytes:
                        newid = hash_util.generate_random_key().key
                        self.segment_ids.append(newid)

                        seg_hash = hash_util.Key(newid)
                        self.messages.append(
                            Message_Forward(self.node_info,seg_hash,
                                Database_Put_Message(self.node_info,seg_hash, keyfile_hash,  str(keyfile_hash)+"\n"+bytes)))

                        bytes = f.read(self.segment_size)
                finally:
                    f.close()

            self.sw_reading.stop()
            self.sw_queuing = Stopwatch()
            keyfile = "KEYFILE\n"+self.filename+"\n"+reduce(lambda x,y: x+"\n"+y,self.segment_ids)
            self.messages.appendleft( Message_Forward(self.node_info,keyfile_hash,Database_Put_Message(self.node_info, keyfile_hash, keyfile_hash, keyfile)))
            self.sw_queuing.stop()
        except:
            show_error()

    def send(self,service):
        while self.messages:
            msg = self.messages.pop()
            service.send_message(msg)

    def confirm(self,msg):
        if self._confirmed == 0:
            self.sw_confirming = Stopwatch()

        self._confirmed += 1

        if self._confirmed == len(self.segment_ids) + 1: # +1 for key-file response
            #self.sw_confirming.elapsed("msg confirming " + self.filename)
            #self.sw_reading.elapsed("disk read " + self.filename)
            #self.sw_queuing.elapsed("msg queuing " + self.filename)
            self.sw_total.elapsed("Wrote " + self.filename)
            return True
        return False


class File_Service(Service):
    """This object is intented to act as a parent/promise for Service Objects"""
    upload_files = {}
    exit = False
    def __init__(self, message_router):
        super(File_Service, self).__init__(SERVICE_FILE, message_router)
        self.partial_files = {}
        self._coro_file_writer = Coro(self._file_writer_coro)

    def _file_writer_coro(self, coro=None):
        coro.set_daemon()
        thread_pool = AsynCoroThreadPool(2 * multiprocessing.cpu_count())
        while not self.exit:
            try:
                node_info, filename, segment_size = yield coro.receive()
                if not filename:
                    break

                task = Upload_File_Task(node_info,filename,segment_size)
                yield thread_pool.async_task(coro, task.process_file)
                self.upload_files[hash_util.hash_str(filename)] = task
                task.send(self)
            except:
                show_error()

    def stop(self):
        self.exit = True
        self._coro_file_writer.send((None,None,None))

    def read(self,node_info, filename):
        # initiate a file download
        filehash = hash_util.hash_str(filename)
        self.partial_files[str(filehash)] = Partial_file(filename)
        self.send_message(Message_Forward(node_info, filehash, Database_Get_Message(node_info, filehash)))

    def store(self, node_info, filename, segment_size=128):
        # queue for async execution since it requires blocking I/O
        self._coro_file_writer.send((node_info, filename, segment_size))

    def handle_message(self, msg):
        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        if not msg.dest_service == self.service_id:
            raise Exception("Mismatched service recipient for message.")
        elif msg.type == Database_Put_Message_Response.Type():
            # placeholder but will allow us to get exact storage times across the network if we determine when all sent hashes have a response
            print "Write block requested by " + str(msg.origin_node) + " was fulfilled by " + str(msg.storage_node)
            if self.upload_files.has_key(msg.keyfile_hash):
                if self.upload_files[msg.keyfile_hash].confirm(msg):
                    del self.upload_files[msg.keyfile_hash]
            else:
                raise Exception("Unexpected keyfile hash")
        elif msg.type == Database_Get_Message_Response.Type():
            # placeholder but will allow us to get exact storage times across the network if we determine when all requested hashes have a response
            #print "Read block requested by " + str(msg.origin_node) + " was fulfilled by " + str(msg.storage_node)

            fileid = msg.destination_key
            contents = msg.file_contents
            if len(contents) > 7 and contents[:7] == "KEYFILE":
                partial = self.partial_files[str(fileid)]
                partial.add_key(contents)
                for k in partial.chunklist:
                    # determine where the next part of this file is stored
                    self.send_message(Message_Forward(msg.origin_node,hash_util.Key(k),Database_Get_Message(msg.origin_node, hash_util.Key(k))))
            elif contents == "404 Error":
                print contents
            else:
                #print contents
                addr, cont = contents.split("\n",1)
                if addr in self.partial_files.keys():
                    partial = self.partial_files[addr]
                    partial.input_stream.put(msg)
                    if partial.process_queue():
                        print partial.get_file(True)
                        partial.sw.elapsed("read " + partial.filename)

        elif msg.type == Message_Console_Command.Type():
            self.handle_command(msg)

    def attach_to_console(self):
        ### return a list of command-strings
        return ["store","read"]

    def handle_command(self, msg):
        if msg.command == "store" and len(msg.args) == 1:
            if not hash_util.hash_str(msg.args[0]) in self.upload_files.keys():
                self.store(msg.console_node.thisNode, msg.args[0])
            else:
                print "Store is already in progress for this file."
        elif msg.command == "read" and len(msg.args) == 1:
            self.read(msg.console_node.thisNode, msg.args[0])
