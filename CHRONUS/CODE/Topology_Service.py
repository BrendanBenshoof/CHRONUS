from service import *
from message import *
import node
import hash_util
from math import pi


class Toplogy_Poll_Message(Message):
    def __init__(self, origin_node, destination_key):
        Message.__init__(self)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.service = "TOPOLOGY"
        self.type =  "TOPOLOGY"
        self.add_content("server_list",[str(origin_node)])
        self.add_content("link_list",{})
        self.add_content("start",origin_node.key)
        self.add_content("end",destination_key)
        self.reply_to = origin_node


class Topology(Service):
    def __init__(self):
        super(Service, self).__init__()
        self.service_id = "TOPOLOGY"
        self.topology_guess = []

    def get_my_links(self):
        output = []
        for n in node.fingerTable:
            if not str(n) in output:
                output.append(str(n))
        return output

    def start_inquery(self):
        sucessor_cheat = hash_util.generate_lookup_key_with_index(self.owner.key,0)
        new_query = Toplogy_Poll_Message(self.owner,sucessor_cheat)
        linkset = {str(node.thisNode): self.get_my_links()}
        new_query.add_content("link_list",linkset)
        self.send_message(new_query)
        print "Send Inquery"

    def attach_to_console(self):
        ### return a dict of command-strings
        return ["plot"]

    def handle_command(self, comand_st, arg_str):
        ### one of your commands got typed in
        self.start_inquery()


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
            linkset = msg.get_content("link_list")
            if not msg.reply_to == self.owner:
                if  not hash_util.hash_between(self.owner.key,start,end):
                    sucessor_cheat = hash_util.generate_lookup_key_with_index(self.owner.key,0)
                    msg.origin_node = self.owner
                    msg.destination_key = sucessor_cheat
                    record.append(str(self.owner))
                    linkset[str(node.thisNode)] = self.get_my_links()
                    msg.add_content("server_list", record)
                    msg.add_content("link_list",linkset)
                    self.send_message(msg)
                else:
                    msg.destination_key = msg.reply_to.key
                    self.send_message(msg, msg.reply_to)
            else:
                print "render inquery"
                render(record, linkset)

def render(record, edges):
    import matplotlib.pyplot as plt
    import networkx as nx
    G = nx.DiGraph()
    G.add_nodes_from(record)
    print record
    print edges
    for n in record:
        for k in edges[str(n)]:
            G.add_edge(n,k)
    G.remove_node("None")
    nx.draw_circular(G, with_labels=True)
    plt.show()
