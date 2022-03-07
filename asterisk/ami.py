import socket
import asyncio
import json


class Ami:
    def __init__(self, log):
        self.event = None
        self.buffer = 4096 * 4
        self.__reader = None
        self.__writer = None
        self.__loop = None
        self.__log = log

    async def connect(self, host='127.0.0.1', port=5038):
        self.__reader, self.__writer = await asyncio.open_connection(host, port)
        self.__loop = asyncio.get_running_loop()

    async def login(self, user=None, secret=None):
        await asyncio.sleep(0.5)
        if (user != None and secret != None):
            message = f"Action:Login\r\nUsername:{user}\r\nSecret:{secret}\r\n\r\n"
            self.__writer.write(message.encode("utf-8"))
            await self.__writer.drain()

    async def run(self, subscriber):
        await asyncio.sleep(1)

        data = await self.__reader.read(self.buffer)
        self.event = self._event_format(data.decode("utf-8"))

        if (self.event["Response"] == "Success"):
            self.__log.log(msg="Conectado ao manager do asterisk")
            while True:
                data = await self.__reader.read(self.buffer)

                self.event = self._event_format(data.decode("utf-8"))

                if (self.event["Event"] == "PeerStatus"):
                    if (self.event["PeerStatus"] == "Registered"):
                        subscriber.notify_all(json.dumps(self.event))

                        msg = "ramal {0} registrado no IP {1}".format(
                            self.event["Peer"],
                            self.event["Address"]
                        )

                    if (self.event["PeerStatus"] == "Unregistered"):
                        subscriber.notify_all(json.dumps(self.event))

                        msg = "ramal {0} desregistrado".format(
                            self.event["Peer"]
                        )

                    self.__log.log(msg=msg)

                if (self.event["Event"] == "Newstate" and self.event["ChannelState"] == "4"):
                    subscriber.notify_all(json.dumps(self.event))

                    msg = "ramal {0} esta iniciando ligação".format(self.event["CallerIDNum"])

                    self.__log.log(msg=msg)

                if (self.event["Event"] == "DialBegin" and self.event["ChannelState"] == "4"):
                    subscriber.notify_all(json.dumps(self.event))

                    msg = "ramal {0} esta ligando para {1}".format(
                        self.event["CallerIDNum"],
                        self.event["DestCallerIDNum"]
                    )

                    self.__log.log(msg=msg)

                if (self.event["Event"] == "DialState" and self.event["DestChannelState"] == "5" and self.event.get("CallerIDNum")):
                    subscriber.notify_all(json.dumps(self.event))

                    msg = "ramal {0} esta recebendo ligacao do {1}".format(
                        self.event["DestCallerIDNum"],
                        self.event["CallerIDNum"]
                    )

                    self.__log.log(msg=msg)

                if (self.event["Event"] == "DialEnd" and self.event.get("CallerIDNum")):
                    subscriber.notify_all(json.dumps(self.event))

                    msg = "ramal {0} {1} chamada do ramal {2}".format(
                        self.event["DestCallerIDNum"],
                        self.event["DialStatus"],
                        self.event["CallerIDNum"]
                    )

                    self.__log.log(msg=msg)

                if (self.event["Event"] == "Hangup"):
                    subscriber.notify_all(json.dumps(self.event))

                    msg = "ramal {0} desligou".format(
                        self.event["CallerIDNum"]
                    )

                    self.__log.log(msg=msg)

    def _event_format(self, event):
        if "Asterisk Call Manager" in event:
            info_list = [s.replace(" ", "").split(":", 1) for s in event.split("\r\n") if s][1:]
        else:
            info_list = [s.replace(" ", "").split(":", 1) for s in event.split("\r\n") if s]

        return dict(info_list)
