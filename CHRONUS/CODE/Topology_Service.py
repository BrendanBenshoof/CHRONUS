from service import *
from message import *
import node
import hash_util
from math import pi
import matplotlib
import numpy as np
from matplotlib.pyplot import figure, show, grid

class Toplogy_Poll_Message(Message):
    def __init__(self, origin_node, destination_key):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.service = "TOPOLOGY"
        self.type =  "TOPOLOGY"
        self.add_content("server_list",[origin_node])
        self.add_content("start",origin_node.key)
        self.add_content("end",destination_key)
        self.reply_to = origin_node


class Topology(Service):
    def __init__(self):
        super(Service, self).__init__()
        self.service_id = "TOPOLOGY"
        self.topology_guess = []

    def start_inquery(self):
        sucessor_cheat = hash_util.generate_lookup_key_with_index(self.owner.key,0)
        new_query = Toplogy_Poll_Message(self.owner,sucessor_cheat)
        self.send_message(new_query)
        print "Send Inquery"

    def handle_message(self, msg):
            print "get inquery"
            """This function is called whenever the node recives a message bound for this service"""
            """Return True if message is handled correctly
            Return False if things go horribly wrong
            """
            if msg.service != self.service_id:
                return False
            start = msg.get_content("start")
            end = msg.get_content("end")
            record = msg.get_content("server_list")
            if not msg.reply_to == self.owner:
                if  not hash_util.hash_between(self.owner.key,start,end):
                    sucessor_cheat = hash_util.generate_lookup_key_with_index(self.owner.key,0)
                    msg.origin_node = self.owner
                    msg.destination_key = sucessor_cheat
                    record.append(self.owner)
                    msg.add_content("server_list", record)
                    self.send_message(msg)
                else:
                    msg.destination_key = msg.reply_to.key
                    self.send_message(msg, msg.reply_to)
            else:
                print "render inquery"
                render(record)

def render(record):
    length = len(record)
    thetas = []
    radii = map( lambda x: 0.5, record)
    print thetas
    print radii
    for r in record:
        x = int(r.key.key,16)
        better_num = (2*pi*(x >> 80))/(0x01<<80)
        thetas.append( better_num)
    fig = figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
    ax.plot(thetas, radii, "*")
    for i in map(lambda x, y: (x,y), record, thetas):
        ax.annotate(i[0].IPAddr+":"+str(i[0].ctrlPort), xy=(i[1],0.5))
 
    show()
