from asterisk.ami import Ami
from network.event import Event
from network.connections import run_socket_server, run_websocket_server
from config.log import Log
from config.tlsconfig import get_context_tls
import asyncio
import threading

log = Log()
event = Event(log)

async def init(event, log):
    ami = Ami(log)
    context = get_context_tls()

    tasks = [
                asyncio.create_task(run_socket_server(event, log, context)),
                asyncio.create_task(run_websocket_server(event,log)),
                asyncio.create_task(ami.connect(host='IP_MANAGER_ASTERISK')),
                asyncio.create_task(ami.login(user="USER", secret="PASSWORD")),
                asyncio.create_task(ami.run(event))
            ]

    await asyncio.gather(*tasks)


def run(event, log):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(init(event, log))


thread1 = threading.Thread(target=run, args=(event, log))
thread1.start()
