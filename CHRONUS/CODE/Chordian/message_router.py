from service_message import *
from constants import *
from collections import deque
from threading import Event
from asyncoro import AsynCoro, Coro, AsynCoroThreadPool, logger
import multiprocessing
import logging

class Message_Router():
    _instance = None
    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = Message_Router( )
        return cls._instance

    _commands = None
    exit = False
    def __init__(self):
        self._services = {}

        logger.setLevel(logging.INFO)

        # thread pool -- will burn up if services use the thread for blocking & totally
        # kill application communication. If you have to block for I/O then you better
        # be using async in the destination service
        #for i in range(2 * multiprocessing.cpu_count()) :
        #self._coro_dispatcher = \
        self._dispatcher_coro = Coro(self._message_dispatcher)

    def _message_dispatcher(self, coro=None):
        coro.set_daemon()
        while not self.exit:
            try:
                message = yield coro.receive()

                if self.exit:  #abandon any work & just cleanly exit
                    break

                if message.dest_service in self._services.keys():
                    sw = Stopwatch()
                    self._services[message.dest_service].handle_message(message)

                    if message.type == Message_Recv_Peer_Data.Type():
                        logger.debug( "ROUTER: net receiving " + message.network_msg.Type())
                    elif message.type == Message_Send_Peer_Data.Type():
                        logger.debug( "ROUTER: net dispatching " + message.network_msg.Type())
                    else:
                        logger.debug( "ROUTER: dispatching " + message.Type())

                    # for long running tasks (CPU-bound) you should pass off to a dedicated thread or tune
                    # for I/O bound tasks you should queue the work until an I/O thread-pool thread can handle it
                    if sw.ms() > 1000:
                        print "BUG!!! %s(%s) took %0.3f ms -- FIX IT!!'" % (message.dest_service, message.Type(), sw.ms())
                else:
                    print "Unregistered service '" + message.service + "'"
            except:
                show_error()

        print "Coro(_message_dispatcher) exiting"

    def register_service(self, service_id, service):
        if not service_id in self._services.keys():
            self._services[service_id] = service

    def route(self, message):
        #if message.dest_service in self._services.keys():
        #    self._services[message.dest_service].handle_message(message)
        #pass

        self._dispatcher_coro.send(message)

    def stop(self):
        self.exit = True

        # tell all my services to stop
        for service in self._services.values():
            try:
                service.stop()
            except:
                show_error()

        self._dispatcher_coro.send(None)
        time.sleep(.1)
        AsynCoro.instance().terminate()

    def attach_console(self):
        while True:
            try:
                cmd = raw_input()
            except EOFError: #the user does not have a terminal
                return

            if cmd == "q" or cmd == "Q" or cmd == "quit" or cmd == "exit":
                print "Exiting..."
                break

            try:
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
            except:
                show_error()



