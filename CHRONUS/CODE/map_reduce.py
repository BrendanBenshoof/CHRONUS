from service import *
from message import *
from hash_util import *
import node

MAP_REDUCE = "MAP_REDUCE"
MAP = "MAP"
REDUCE = "REDUCE"


def disribute_fairly(atoms):#do not trust yet
    distribution = {}
    for a in atoms:
        dest = node.find_ideal_forward(a.hashkeyID)
        try:
            distribution[str(dest)].append(a)
        except KeyError:
            distribution[str(dest)] = [a]
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
        return self.service_id

    def handle_message(self, msg):
        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        #if not msg.service == self.service_id:
        #    raise "Mismatched service recipient for message."
        if msg.type == MAP:
            stuff_to_map = msg.dataset
            map_func = msg.map_function
            reduce_func = msg.reduce_function
            results = []
            for a in stuff_to_map:
                results.append(map_func(a))
            if len(results) > 1:
                final_result = reduce_function(reduce_func, results)
            else:
                final_result = results[0]
            newmsg = Reduce_Message(msg.jobid, final_result, reduce_func)
            newmsg.destination_key = msg.reply_to.key
            self.send_message(newmsg, msg.reply_to)
        elif msg.type == REDUCE:
            jobid = msg.jobid
            print "in reduce",jobid
            atom = msg.dataAtom
            myreduce = msg.reduce_function
            if jobid in self.temp_data.keys():
                self.temp_data[jobid] = myreduce(atom, self.temp_data[jobid])
            else:
                self.temp_data[jobid] = atom

        return msg.service == self.service_id

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
            print self.temp_data.keys()
            
            if jobid in self.temp_data.keys():
                if len(args) >1:
                    f = file(args[1],"w+")
                    f.write(str(self.temp_data[jobid].contents))
                    print "wrote to: ",f
                    f.close()
                else:
                    print self.temp_data[jobid].contents
            else:
                "no value on this job"

        return None

    def send_message(self, msg, dest=None):
        self.callback(msg, dest)

    def change_in_responsibility(self,new_pred_key, my_key):
        pass #this is called when a new, closer predicessor is found and we need to re-allocate
            #responsibilties
    
    def test(self):
        import test
        jobid = hash_str("job")
        jobs = test.stage()
        map_func = test.map_func
        reduce_func = test.reduce_func
        for a in jobs:
            msg = Map_Message(jobid, [a], map_func, reduce_func)
            msg.reply_to = self.owner
            self.send_message(msg,None)



class Map_Message(Message):
    def __init__(self, jobid, dataset, map_function, reduce_function):
        super(Map_Message, self).__init__(MAP_REDUCE, MAP)
        self.jobid = jobid
        self.map_function = map_function  #store you function here
        self.dataset = dataset  #list of atoms
        self.reduce_function = reduce_function


class Reduce_Message(Message):
    def __init__(self, jobid, dataAtom, reduce_function):
        super(Reduce_Message, self).__init__( MAP_REDUCE, REDUCE)
        self.jobid = jobid
        self.dataAtom = dataAtom  #list of atoms
        self.reduce_function = reduce_function


def cry():
    print("Your code is bad, and you should feel bad. https://www.youtube.com/watch?v=BSKVEkMiTMI")

##########Brendan's work starts

