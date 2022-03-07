from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
from abc import ABCMeta, abstractmethod
from config.auth import *
import asyncio

class Client(metaclass=ABCMeta):

    @abstractmethod
    def notify(self, jinfo_event):
        pass

class SocketServer(Client, asyncio.Protocol):
    def __init__(self, subscriber, log):
        self.__subscriber = subscriber
        self.__log = log
        self.__socket_server = None
        self.__is_authenticated = False
        self.type = "Socket"
        self.is_closed = False
        self.peername = None


    def __call__(self):
        return self

    def connection_made(self, transport):
        self.__socket_server = transport
        self.peername = transport.get_extra_info('peername')
        self.__log.log(msg=f'conexao via {self.type} de {self.peername}')
        self.__subscriber.register(self)

    def connection_lost(self, execption):
        self.is_closed = True
        self.__subscriber.deregister_all_closed()

    def data_received(self, data):
        msg = data.decode("utf-8").rstrip("\r\n").lower()

        if authenticate(msg):
            self.__is_authenticated = True
            self.__socket_server.write(bytes("A:authenticated".encode("utf-8")))
        else:
            self.__socket_server.write(bytes("I:not authenticate".encode("utf-8")))


    def notify(self, jinfo_event):
        if self.__is_authenticated:
            self.__socket_server.write(bytes(jinfo_event.encode('utf-8')))

class WebsocketServer(Client, WebSocketServerProtocol):
    def __init__(self, subscriber, log):
        super().__init__()
        self.__subscriber = subscriber
        self.__log = log
        self.type = "Websocket"
        self.peername = None

    def __call__(self):
        return self

    def notify(self, jinfo_event):
        self.sendMessage(bytes(jinfo_event.encode('utf-8')))

    def onConnect(self, request):
           self.__log.log(msg=f"conexao via {self.type} de {request.peer}")
           self.peername = request.peer
           self.__subscriber.register(self)

    def onOpen(self):
        self.__log.log(msg=f"{self.type} aberto para cliente {self.peername}")

    def onMessage(self, payload, isBinary):
        pass

    def onClose(self, wasClean, code, reason):
        pass


async def run_socket_server(subscriber, log, context):
    loop = asyncio.get_running_loop() #Excecao RuntimeError
    server = await loop.create_server(
                                SocketServer(subscriber, log),
                                '0.0.0.0',
                                50000,
                                ssl=context
                                )
    await server.serve_forever()

async def run_websocket_server(subscriber, log):
    factory = WebSocketServerFactory()
    factory.protocol = WebsocketServer(subscriber, log)

    loop = asyncio.get_event_loop()
    server = await loop.create_server(factory, '0.0.0.0', 40000)

    try:
        await server.serve_forever()
    except KeyboardInterrupt:
        pass
