from service import *
from message import *
from hash_util import *
import Queue
import node
from threading import Thread
import time

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

class Data_Atom(object):
    def __init__(self, jobid, hashkeyID, contents):
        self.jobid = hash_str(jobid)
        if hashkeyID is None:
            self.hashkeyID = generate_random_key()
        else:
           self.hashkeyID = hashkeyID
        self.contents = contents
        #print hashkeyID

##test for distribute 


job_todo = Queue.Queue()


class Map_Reduce_Service(Service):
    """This object is intented to act as a parent/promise for Service Objects"""
    def __init__(self):
        super(Map_Reduce_Service,self).__init__()
        self.service_id = "MAP_REDUCE"
        self.temp_data = {}

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
            job_todo.put(msg)
            return True
        else:
            return False

    def attach_to_console(self):
        ### return a list of command-strings
        return ["test","results"]

    def handle_command(self, comand_st, arg_str):
        ### one of your commands got typed in

        if comand_st == "test":
            self.test()
        if comand_st == "results":
            args = arg_str.split(" ")
            jobid = hash_str(args[0])
            print jobid            
            if jobid in self.temp_data.keys():
                if len(args) >1:
                    f = file(args[1],"w+")
                    f.write(str(self.temp_data[jobid].contents))
                    print "wrote to: ",f
                    f.close()
                else:
                    print "results:",self.temp_data[jobid].contents
            else:
                print "no value on this job"

        return None

    def send_message(self, msg, dest=None):
        self.callback(msg, dest)

    def change_in_responsibility(self,new_pred_key, my_key):
        pass #this is called when a new, closer predicessor is found and we need to re-allocate
            #responsibilties
    
    def test(self):
        import pi
        jobid = hash_str("pi")
        jobs = pi.stage()
        jobs_withdest = disribute_fairly(jobs)
        map_func = pi.map_func
        reduce_func = pi.reduce_func
        for k in jobs_withdest.keys():
            msg = Map_Message(jobid, jobs_withdest[k], map_func, reduce_func)
            msg.reply_to = self.owner
            self.send_message(msg,k)

    def Mapreduce_worker(self):
        while True:
            time.sleep(0.1)
            newjob = job_todo.get(True)
            if newjob.type == MAP:
                self.domap(newjob)
                job_todo.task_done()
            if newjob.type == REDUCE:
                self.doreduce(newjob)
                job_todo.task_done()

    def doreduce(self,msg):
            jobid = msg.jobid
            print "in reduce",jobid
            atom = msg.dataAtom
            myreduce = msg.reduce_function
            if jobid in self.temp_data.keys():
                self.temp_data[jobid] = myreduce(atom, self.temp_data[jobid])
            else:
                self.temp_data[jobid] = atom

    def domap(self,msg):
        #forward stuff I do not care about first
        forward_dests = disribute_fairly(msg.dataset)
        stuff_to_map = None
        print "I got a map request, am forwarding to:",map( lambda x: str(x.key), forward_dests.keys())
        for k in forward_dests.keys():
            if k != self.owner:
                print "I am forwarding: ",len(forward_dests[k])
                newmsg = Map_Message(msg.jobid, forward_dests[k], msg.map_function, msg.reduce_function)
                newmsg.reply_to = msg.reply_to
                self.send_message(newmsg, k)
            else:
                stuff_to_map = forward_dests[k]
        if stuff_to_map:
            map_func = msg.map_function
            reduce_func = msg.reduce_function
            results = map(map_func, stuff_to_map)
            if len(results) > 1:
                final_result = reduce(reduce_func, results)
            else:
                final_result = results[0]
            newmsg = Reduce_Message(msg.jobid, final_result, reduce_func)
            newmsg.destination_key = msg.reply_to.key
            self.send_message(newmsg, msg.reply_to)


class Map_Message(Message):
    def __init__(self, jobid, dataset, map_function, reduce_function):
        super(Map_Message, self).__init__(MAP_REDUCE, MAP)
        self.jobid = jobid
        self.map_function = map_function  #store you function here
        self.dataset = dataset  #list of atoms
        self.reduce_function = reduce_function
        self.type = MAP


class Reduce_Message(Message):
    def __init__(self, jobid, dataAtom, reduce_function):
        super(Reduce_Message, self).__init__( MAP_REDUCE, REDUCE)
        self.jobid = jobid
        self.dataAtom = dataAtom  #single atom
        self.reduce_function = reduce_function
        self.type = REDUCE


def cry():
    print("Your code is bad, and you should feel bad. https://www.youtube.com/watch?v=BSKVEkMiTMI")

##########Brendan's work starts

