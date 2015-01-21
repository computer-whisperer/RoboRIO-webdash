from networktables import NetworkTable
import asyncio
from aiohttp import web

update_wait = .1
ip_address = "10.1.0.101"

initialized_networktables = False

tables = dict()
root_table = None

connections = list()

def table_listener(source, key, value, isNew):
    if source not in tables:
        tables[source] = {}
    tables[source][key] = value

    for connection in connections:
        connection.pending_updates.append({})


def setup_networktables(ip):
    if initialized_networktables:
        return
    NetworkTable.setIPAddress(ip)
    NetworkTable.setClientMode()
    NetworkTable.initialize()
    root_table = NetworkTable.getTable("SmartDashboard")
    root_table.addTableListener(table_listener, True)

@asyncio.coroutine
def networktables_websocket(request):
    #Setup websocket
    ws = web.WebSocketResponse()
    ws.start(request)


    #Setup networktables
    setup_networktables(ip_address)

    connections.append({"socket": ws, "pending_updates": list()})

    last_data = dict()
    #Update periodically until the websocket is closed.

    while True:
        try:
            #Send updates
            pass
        except web.WSClientDisconnectedError:
            return ws
        yield from asyncio.sleep(.1)



