import sys, os
sys.path.insert(0,os.path.join(os.path.dirname(__file__), 'Chordian'))
from network_service import Network_Service
from message import *
import node
from node_service import Node_Info

class Hijack_Network():
    _instance = None
    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = Hijack_Network( )
        return cls._instance

    def __init__(self,HOST="localhost",PORT=9000):
        self.network_service = Network_Service(self)  # I'm my own message router
        self.network_service.handle_message(Message_Start_Server(HOST, PORT))

    def stop(self):
        self.network_service.handle_message(Message_Stop_Server(HOST, PORT))

    def route(self, message):
        if message.type == Message_Recv_Peer_Data.Type():
            node.handle_message(message.network_msg)
    def register_service(self, service_id, instance):
        pass

    def send_message(self,msg,dest):
        self.network_service.handle_message(Message_Send_Peer_Data(dest,msg))


if __name__ == "__main__":

    hj = Hijack_Network( "",  9000 )
    hj.send_message( Update_Message(None, None, 0), Node_Info("127.0.0.1", 9001 ) )