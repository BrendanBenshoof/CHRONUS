
class Message_Router():
    def __init__(self):
        self._services = {}

    def register_service(self, service_id, service):
        if not self._services[service_id]:
            self._services[service_id] = service

    def route(self, message):
        if self._services[message.service]:
            self._services[message.service].handle_message(message)



