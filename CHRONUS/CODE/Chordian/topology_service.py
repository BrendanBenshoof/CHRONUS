from super_service import *
from service_message import *
from constants import *

class Topology_Poll_Message(Message):
    @classmethod
    def Type(cls): return "TOPOLOGY"

    def __init__(self, origin_node, destination_key):
        super(Topology_Poll_Message, self).__init__(self,SERVICE_TOPOLOGY,Topology_Poll_Message.Type())
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.add_content("server_list",[str(origin_node)])
        self.add_content("link_list",{})
        self.add_content("start",origin_node.key)
        self.add_content("end",destination_key)
        self.reply_to = origin_node


class Topology_Service(Service):
    def __init__(self,message_router):
        super(Topology_Service, self).__init__(SERVICE_TOPOLOGY,message_router)
        self.topology_guess = []
"""
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

"""

    #def handle_message(self, msg):
   #     print "get inquery"
"""This function is called whenever the node recives a message bound for this service"""
"""Return True if message is handled correctly
Return False if things go horribly wrong
"""
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
"""
def render(record, edges):
    """
    import matplotlib.pyplot as plt
    import math
    record_matrix = map(lambda x: x.split(":"), record)
    myMax = int(2**160)
    x_points = [0.0]
    y_points = [0.0]
    names = ["origin"]
    print record_matrix
    for r in record_matrix:
        name = str(r[0])+":"+str(r[1])
        int_id = int(r[2][2:],16)
        ratio = int_id*1.0/myMax
        theta = math.pi*2.0*ratio
        x = math.sin(theta)
        y = math.cos(theta)
        print x, y, name
        x_points.append(x)
        y_points.append(y)
        plt.annotate(name, xy = (x, y))
    plt.plot(x_points,y_points,"o")
    plt.show()
    """
    pass