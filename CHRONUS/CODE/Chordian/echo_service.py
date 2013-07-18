from super_service import Service
from constants import *

class Echo_Service(Service):
    def __init__(self, message_router):
        super(Echo_Service, self).__init__(SERVICE_ECHO, message_router,cl_name="echo")

    def handle_message(self, msg):
        if not msg.service == self.service_id:
            raise Exception("Mismatched service recipient for message.")

        for k in msg.contents.keys():
            print msg.get_content(k)