from networktables import NetworkTable
import asyncio
import json
from aiohttp import web
from threading import RLock

import logging
logging.basicConfig(level=logging.DEBUG)

update_wait = .1
ip_address = "127.0.0.1"

initialized_networktables = False

table_data = None
table_data_lock = RLock()
root_table = None

connections = list()
tagged_tables = list()

def subtable_listner(source, key, value, isNew):
    print("subTableListener triggered! params: '{}', '{}', '{}', '{}'".format(source, key, value, isNew))
    with table_data_lock:
        if source.containsSubTable(key):
            watch_table(value.path)
        else:
            target_ref = table_data
            for s in source.path.split(NetworkTable.PATH_SEPARATOR):
                if s == "":
                    continue
                elif s not in target_ref:
                    target_ref[s] = dict()
                target_ref = target_ref[s]
            target_ref[key] = source.getValue(key)


def watch_table(key):
    print("Watching Table " + key)
    with table_data_lock:
        if key in tagged_tables:
            return
        new_table = root_table.getTable(key)
        new_table.addSubTableListener(subtable_listner)
        #new_table.addTableListener(val_listener, True)


def setup_networktables(ip=ip_address):
    global root_table, table_data, initialized_networktables
    if initialized_networktables:
        return
    NetworkTable.setIPAddress(ip)
    NetworkTable.setClientMode()
    NetworkTable.initialize()
    root_table = NetworkTable.getTable("")
    root_table.addSubTableListener(subtable_listner)
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

    last_data = dict()

    #Update periodically until the websocket is closed.
    try:
        while True:
            updates = dict_delta(last_data, table_data)
            if len(updates) > 0:
                string_data = json.dumps(updates)
                print("Sending " + string_data)
                ws.send_str(string_data)
                last_data = table_data.copy()
            if ws.closing:
                break
            yield from asyncio.sleep(update_wait)
    except web.WSClientDisconnectedError:
        pass

    print("NT Websocket {} Disconnected".format(con_id))
    with table_data_lock:
        connections.remove(connection)
    return ws

def dict_delta(dict_a, dict_b):
    result = dict()
    for k in dict_b:
        if k in dict_a:
            if isinstance(dict_a[k], dict) and isinstance(dict_b[k], dict):
                comp_res = dict_delta(dict_a[k], dict_b[k])
                if len(comp_res) > 0:
                    result[k] = comp_res
            elif dict_a[k] != dict_b[k]:
                result[k] = dict_b[k]
        else:
            result[k] = dict_b[k]
    return result




@asyncio.coroutine
def networktables_websocket_listener(ws):
    try:
        while True:
            jdata = yield from ws.receive_str()
            data = json.loads(jdata)
            root_table.pushData(data["name"], data["value"])
    except web.WSClientDisconnectedError:
        pass