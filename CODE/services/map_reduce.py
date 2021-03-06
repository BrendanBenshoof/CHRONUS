from service import *
from message import *
from hash_util import *


import Queue
import node
from threading import Thread
import time
import importlib

MAP_REDUCE = "MAP_REDUCE"
MAP = "MAP"
REDUCE = "REDUCE"


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

##test for distribute 


job_todo = Queue.Queue()

backups = []

reduce_todo = Queue.Queue()


class Map_Reduce_Service(Service):
    """This object is intended to act as a parent/promise for Service Objects"""
    def __init__(self):
        super(Map_Reduce_Service,self).__init__()
        self.service_id = "MAP_REDUCE"
        self.temp_data = {}
        self.job_records = {}

    def attach(self, owner, callback):
        """Called when the service is attached to the node"""
        """Should return the ID that the node will see on messages to pass it"""
        self.callback = callback
        self.owner = owner
        for i in range(0,1):
            t = Thread(target=self.Mapreduce_worker)
            t.daemon = True
            t.start()
        return self.service_id

    def handle_message(self, msg):
        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        #if not msg.service == self.service_id:
        #    raise "Mismatched service recipient for message."
        if msg.service == self.service_id:
            if msg.type==MAP and msg.backup: #short circuited and to avoid typeerror
                pass
                #backups.append(msg)
                #print "sent a backup map"
            elif msg.type==MAP:
                #msg.backup = True
                #self.send_message(msg,node.successor)
                job_todo.put(msg)
            else:
                job_todo.put(msg)
            return True
        else:
            return False

    def attach_to_console(self):
        ### return a list of command-strings
        return ["do","results", "clear"]

    def handle_command(self, comand_st, arg_str):
        ### one of your commands got typed in

        if comand_st == "do":
            self.test(arg_str)
        if comand_st == "results":
            args = arg_str.split(" ")
            jobid = hash_str(args[0])
            print jobid            
            if jobid in self.temp_data.keys():
                r = file(str(jobid)+".record","w+")
                r.write(self.job_records[jobid])
                r.close()
                if len(args) >1:
                    f = file(args[1],"w+")
                    f.write(str(self.temp_data[jobid].contents))
                    print "wrote to: ",f
                    f.close()
                else:
                    print "results:",self.temp_data[jobid].contents
            else:
                print "no value on this job"
        if comand_st =="clear":
            self.job_records = {}
            self.temp_data = {}
            backups = []

        return None


    def change_in_responsibility(self,new_pred_key, my_key):
        return
        print "checking my backupped work"
        for b in backups:
            if b.timestamp < time.time()-b.keepalive:
                if hash_between(b.destination_key, new_pred_key, my_key):
                    print "gonna do a backup"
                    job_todo.put(b)
                    backups.remove(b)
                    b.backup = True
                    self.send_message(b,node.successor)
            else:
                backups.remove(b)
                

    
    def test(self, to_test):
        X = importlib.import_module("."+to_test,"tests")
        print X
        jobid = hash_str(to_test)
        jobs = X.stage()
        
        map_func = X.map_func
        reduce_func = X.reduce_func
        those_that_remain = self.polite_distribute(jobid, jobs, map_func, reduce_func, self.owner)
        msg = Map_Message(jobid,those_that_remain, map_func, reduce_func)
        msg.reply_to = self.owner
        msg.origin = self.owner
        self.send_message(msg,self.owner)


    def Mapreduce_worker(self):
        while True:
            newjob = job_todo.get(True)
            print job_todo.qsize()
            if newjob.type == MAP:
                self.domap(newjob)
                job_todo.task_done()
            elif newjob.type == REDUCE:
                if node.I_own_hash(newjob.destination_key):
                    self.doreduce(newjob)
                    job_todo.task_done()
                else:
                    reduce_todo.put(newjob)

    def doreduce(self,msg):
            jobid = msg.jobid
            print "in reduce",jobid
            atom = msg.dataAtom
            myreduce = msg.reduce_function
            if jobid in self.temp_data.keys():
                self.temp_data[jobid] = myreduce(atom, self.temp_data[jobid])
                self.job_records[jobid]+="\n-------\n"+msg.timeingRecord
            else:
                self.temp_data[jobid] = atom
                self.job_records[jobid]=msg.timeingRecord+"\n Recived "+str(time.time())+"\n"

    def domap(self,msg):
        #forward stuff I do not care about first
        jobs = msg.dataset
        print len(jobs),"cached"
        stuff_to_map = self.polite_distribute(msg.jobid,jobs, msg.map_function, msg.reduce_function, msg.reply_to)
        print len(stuff_to_map),"I am bothering with"
        starttime = time.time()
        if len(stuff_to_map)>0:
            map_func = msg.map_function
            reduce_func = msg.reduce_function
            results = map(map_func, stuff_to_map)
            if len(results) > 1:
                final_result = reduce(reduce_func, results)
            else:
                final_result = results[0]
            final_result.mapped = True
            newmsg = Reduce_Message(msg.jobid, final_result, reduce_func)
            newmsg.destination_key = msg.reply_to.key
            newmsg.origin = msg.origin
            newmsg.timeingRecord = msg.timeingRecord + "\n--\n" + newmsg.timeingRecord
            newmsg.timeingRecord += "Map start: "+str(starttime)+"\n"+"Map done: "+str(time.time())+"\n"
            self.send_message(newmsg, msg.reply_to)

    def polite_distribute(self, jobid, jobs, map_func, reduce_func, reply_to):
        stuff_to_map = []
        forward_dests = disribute_fairly(jobs)
        print forward_dests.keys()
        if self.owner in forward_dests.keys():
            stuff_to_map = forward_dests[self.owner][:]
            try:
                del forward_dests[self.owner]
            except KeyError:
                pass
        jobs_sent = 0
        jobs_total = len(jobs)-len(stuff_to_map)
        for k in forward_dests.keys():
            msg = Map_Message(jobid,forward_dests[k], map_func, reduce_func)
            msg.origin = reply_to
            msg.reply_to = reply_to
            self.send_message(msg,k)
        return stuff_to_map

class Map_Message(Message):
    def __init__(self, jobid, dataset, map_function, reduce_function):
        super(Map_Message, self).__init__(MAP_REDUCE, MAP)
        self.jobid = jobid
        self.map_function = map_function  #store your function here
        self.dataset = dataset  #list of atoms
        self.reduce_function = reduce_function
        self.origin = None
        self.backup = False
        self.type = MAP
        self.timeingRecord = "'map msg made', "+str(time.time())+"\n"+str(node.thisNode)+"\n"
        self.timestamp = time.time()
        self.keepalive = 60.0*30



class Reduce_Message(Message):
    def __init__(self, jobid, dataAtom, reduce_function):
        super(Reduce_Message, self).__init__( MAP_REDUCE, REDUCE)
        self.jobid = jobid
        self.dataAtom = dataAtom  #single atom
        self.reduce_function = reduce_function
        self.type = REDUCE
        self.timeingRecord = "'reduce msg made', "+str(time.time())+"\n"+str(node.thisNode)+"\n"
        self.backup = False



def cry():
    print("Your code is bad, and you should feel bad. https://www.youtube.com/watch?v=BSKVEkMiTMI")

##########Brendan's work starts

