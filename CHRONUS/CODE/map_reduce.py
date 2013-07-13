from service import *
from message import *
from hash_util import *
import node

MAP_REDUCE = "MAP_REDUCE"
MAP = "MAP"
REDUCE = "REDUCE"


def disribute_fairly(atoms):
    distribution = {}
    for a in atoms:
        dest = node.closest_preceding_node(a.hashkeyID)
        try:
            distribution[str(dest)].append(a)
        except KeyError:
            distribution[str(dest)] = [a]
    return distribution

class Data_Atom(object):
    def __init__(self, jobid, hashkeyID, contents):
        self.jobid = jobid
        self.hashkeyID = hashkeyID
        self.contents = contents

##test for distribute 
def test():
    test_data = map(lambda x: Data_Atom(generate_random_key(),generate_random_key(),generate_random_key()), range(0,10))
    print disribute_fairly(test_data)

class Map_Reduce_Service(Service):
    """This object is intented to act as a parent/promise for Service Objects"""
    def __init__(self):
        super(Map_Reduce_Service,self).__init__()
        self.service_id = MAP_REDUCE

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
        return msg.service == self.service_id

    def attach_to_console(self):
        ### return a list of command-strings
        return ["test_dissiminate"]

    def handle_command(self, comand_st, arg_str):
        ### one of your commands got typed in
        test()
        return None

    def send_message(self, msg, dest=None):
        self.callback(msg, dest)

    def change_in_responsibility(self,new_pred_key, my_key):
        pass #this is called when a new, closer predicessor is found and we need to re-allocate
            #responsibilties




class Map_Message(Message):
    def __init__(self, jobid, dataset, map_function, reduce_function):
        super(Map_Message, self).__init__(self, MAP_REDUCE, MAP)
        self.jobid = jobid
        self.map_function = None  #store you function here
        self.dataset = []  #list of atoms
        self.reduce_function = None

class Reduce_Message(Message):
    def __init__(self):
        super(Reduce_Message, self).__init__(self, MAP_REDUCE, REDUCE)



def cry():
    print("Your code is bad, and you should feel bad. https://www.youtube.com/watch?v=BSKVEkMiTMI")

##########Brendan's work starts

