from networktables import NetworkTable
import asyncio
import json
from aiohttp import web
from threading import RLock

update_wait = .1
ip_address = "127.0.0.1"

initialized_networktables = False

table_data = None
table_data_lock = RLock()
table_object = None

connections = list()

def table_listener(source, key, value, isNew):
    print(source)
    print(key)
    print(value)
    push_table_val(source, key, value)

def push_table_val(source, key, value):
    with table_data_lock:
        if source not in table_data:
            table_data[source] = dict()
        table_data[source][key] = value

        for connection in connections:
            connection["pending_updates"][source][key] = value

def setup_networktables(ip=ip_address):
    global table_object, table_data, initialized_networktables
    if initialized_networktables:
        return
    NetworkTable.setIPAddress(ip)
    NetworkTable.setClientMode()
    NetworkTable.initialize()
    table_object = NetworkTable.getTable("")
    table_object.addSubTableListener(table_listener)
    table_data = dict()
    initialized_networktables = True

@asyncio.coroutine
def networktables_websocket(request):
    #Setup websocket
    ws = web.WebSocketResponse()
    ws.start(request)

    #Setup networktables
    setup_networktables(ip_address)

    #Setup connection dict
    con_id = len(connections)
    with table_data_lock:
        connection = {"socket": ws, "pending_updates": table_data.copy()}
        connections.append(connection)
    print("NT Websocket {} Connected".format(con_id))

    #Start listener coroutine
    asyncio.async(networktables_websocket_listener(ws))

    #Update periodically until the websocket is closed.
    try:
        while True:
            if len(connection["pending_updates"]) > 0:
                string_data = json.dumps(connection["pending_updates"])
                print("Sending " + string_data)
                ws.send_str(string_data)
                connection["pending_updates"] = dict()
            if ws.closing:
                break
            yield from asyncio.sleep(update_wait)
    except web.WSClientDisconnectedError:
        pass

    print("NT Websocket {} Disconnected".format(con_id))
    with table_data_lock:
        connections.remove(connection)
    return ws

@asyncio.coroutine
def networktables_websocket_listener(ws):
    try:
        while True:
            jdata = yield from ws.receive_str()
            data = json.loads(jdata)
            table_object.pushData(data["name"], data["value"])
    except web.WSClientDisconnectedError:
        pass