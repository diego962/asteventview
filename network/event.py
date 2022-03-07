class Event:
    def __init__(self, log):
        self.__clients = []
        self.__log = log

    def register(self, client):
        print(f"registrando client {client}")
        self.__clients.append(client)

    def deregister_all_closed(self):
        aux = []
        
        for client in self.__clients: 
            if not client.is_closed:
                aux.append(client)
            else:
                self.__log.log(msg=f"{client.type} {client.peername} fechou a conexao")
        
        self.__clients = aux

    @property
    def clients(self):
        return self.__clients

    def notify_all(self, jinfo_event):
        for client in self.__clients:
            #data = jinfo_event.encode("utf-8")
            client.notify(jinfo_event)