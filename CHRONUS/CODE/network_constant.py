
class classproperty(object):
     def __init__(self, getter):
         self.getter= getter
     def __get__(self, instance, owner):
         return self.getter(owner)

class Service_Type():
    @classproperty
    def NETWORK_SERVICE(cls): return "NETWORK_SERVICE"


class Peer_Zero_Signal():
    @classproperty
    def TERMINATE(cls): return "TERMINATE"

    @classproperty
    def PEER_CONNECT(cls): return "PEER_CONNECT"

    @classproperty
    def PEER_DISCONNECT(cls): return "PEER_DISCONNECT"

    @classproperty
    def PEER_CONNECTED(cls): return "PEER_CONNECTED"

    @classproperty
    def PEER_DISCONNECTED(cls): return "PEER_DISCONNECTED"

    @classproperty
    def PEER_DATA_SENT(cls): return "PEER_DATA_SENT"

    @classproperty
    def PEER_DATA_RECEIVED(cls): return "PEER_DATA_RECEIVED"


class Message_Type():
    @classproperty
    def START_SERVER(cls): return "START_SERVER"

    @classproperty
    def STOP_SERVER(cls): return "STOP_SERVER"

    @classproperty
    def SEND_PEER_DATA(cls): return "SEND_PEER_DATA"

    @classproperty
    def DISCONNECT_PEER(cls): return "DISCONNECT_PEER"
