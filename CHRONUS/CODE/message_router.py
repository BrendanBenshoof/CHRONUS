from Queue import Queue

class Message_Router():
    _instance = None
    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = Message_Router( )
        return cls._instance

    """
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Message_Router, cls).__new__(
                                cls, *args, **kwargs)
            cls._instance._services = {}

        return cls._instance
    """
    def __init__(self):
        self._services = {}

    def register_service(self, service_id, service):
        if not service_id in self._services.keys():
            self._services[service_id] = service

    def route(self, message):
        if message.service in self._services.keys():
            self._services[message.service].handle_message(message)
        else:
            raise Exception( "Unregistered service '" + message.service + "'" )
