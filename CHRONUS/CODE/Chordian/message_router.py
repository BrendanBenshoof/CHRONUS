from service_message import Message_Console_Command
from constants import *


class Message_Router():
    _instance = None
    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = Message_Router( )
        return cls._instance

    _commands = None
    def __init__(self):
        self._services = {}

    def register_service(self, service_id, service):
        if not service_id in self._services.keys():
            self._services[service_id] = service

    def route(self, message):
        if message.dest_service in self._services.keys():
            self._services[message.dest_service].handle_message(message)
        else:
            raise Exception( "Unregistered service '" + message.service + "'" )

    def attach_console(self):
        while True:
            try:
                cmd = raw_input()
            except EOFError: #the user does not have a terminal
                return

            if cmd == "q" or cmd == "Q":
                break


            node_info = None
            if SERVICE_NODE in self._services.keys():
                node_info = self._services[SERVICE_NODE].get_console_node( )

            args = []
            splitted = cmd.split(' ',1)
            if len(cmd) == 0:  # default action
                self.route(Message_Console_Command(SERVICE_NODE, "print", args, node_info))
            elif len(splitted) == 1:  # try to find a service with the command
                for svc in self._services.values():
                    if splitted[0] in svc.attach_to_console( ):
                        splitted.insert(0,svc.service_id)
                        break

            if len(splitted) > 1:
                svcName = splitted[0]  # consoleName
                command = splitted[1]  # commandName


                # attempt to lookup service by consoleName
                found = False
                for svc in self._services.values():
                    if svc.cl_name == svcName or svc.service_id == svcName:
                        for i in range(2, len(splitted)):
                            args.append( splitted[i] )

                        svc.handle_message(Message_Console_Command(svc.service_id, command, args, node_info))
                        found = True
                        break

                if not found:  # see if a command was entered without a service name
                    for svc in self._services.values():
                        if svcName in svc.attach_to_console():
                            command = svcName
                            for i in range(1, len(splitted)):
                                args.append( splitted[i] )

                            svc.handle_message(Message_Console_Command(svc.service_id, command, args, node_info))
                            found = True
                            break

                if not found:
                    print svcName + " is an unregistered service."




