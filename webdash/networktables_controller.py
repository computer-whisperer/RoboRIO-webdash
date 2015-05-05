from networktables import NetworkTable
from networktables2.type import ArrayData, BooleanArray, NumberArray, StringArray
import asyncio
import json
import math
from aiohttp import web, errors as weberrors
from threading import RLock
from copy import deepcopy

ip_address = "127.0.0.1"

initialized_networktables = False

table_data = dict()
table_data_lock = RLock()
root_table = None

connections = list()
tagged_tables = list()

class ConnectionListener:
    def connected(self, table):
        set_local_value("~CONNECTED~", True)

    def disconnected(self, table):
        set_local_value("~CONNECTED~", False)

def val_listener(key, value, isNew):
    set_local_value(key, value, force_type=True)

def get_local_value(key):
    with table_data_lock:
        if key[0] == NetworkTable.PATH_SEPARATOR:
            key = key[1:]
        value = table_data
        for s in key.split(NetworkTable.PATH_SEPARATOR):
            if isinstance(value, list):
                s = int(s)
                if len(value) <= s:
                    return None
                value = value[s]
            else:
                if s not in value:
                    return None
                value = value[s]
        return value

def set_local_value(key, value, force_type=False):
    with table_data_lock:
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            value = 0.0
        if key[0] == NetworkTable.PATH_SEPARATOR:
            key = key[1:]
        keysplit = key.split(NetworkTable.PATH_SEPARATOR)
        value_key = keysplit[-1:][0]
        table_key = keysplit[:-1]
        target_table = table_data

        for s in table_key:
            if s not in target_table:
                target_table[s] = dict()
            target_table = target_table[s]

        # Save the value if it is new
        if value_key == "":
            return

        if value_key in target_table and not force_type:
            value = type(target_table[value_key])(value)
        if isinstance(target_table, dict):
            target_table[value_key] = value
        elif isinstance(target_table, list):
            target_table[int(value_key)] = value
        else:
            raise ValueError("Unknown Table Type {}".format(type(target_table)))
        trigger_update()

def trigger_update():
    for con in connections:
        con["updated_data"] = True

def set_value(key, value):
    try:
        current_value = get_local_value(key)
        if current_value is not None:
            value = to_type(value, type(current_value))
        if key[0] == NetworkTable.PATH_SEPARATOR:
            key = key[1:]

        # First check if value is part of a list
        parent_object = None
        if NetworkTable.PATH_SEPARATOR in key:
            final_sep_idx = key.rfind(NetworkTable.PATH_SEPARATOR)
            parent_path = key[:final_sep_idx]
            key_end = key[final_sep_idx+1:]
            parent_object = root_table.getValue(parent_path, None)

        if isinstance(parent_object, list):
            parent_object[int(key_end)] = value

            if isinstance(value, bool):
                new_arraydata = BooleanArray()
            elif isinstance(value, float) or isinstance(value, int):
                new_arraydata = NumberArray()
            else:
                new_arraydata = StringArray()

            new_arraydata.extend(parent_object)

            root_table.putValue(parent_path, new_arraydata)
        else:
            if isinstance(value, bool):
                root_table.putBoolean(key, value)
            elif isinstance(value, float) or isinstance(value, int):
                root_table.putNumber(key, value)
            else:
                root_table.putString(key, str(value))
    except Exception as e:
        print(e)
    finally:
        trigger_update()


def to_type(value, target_type):
    value = str(value)
    if target_type is bool:
        return value.lower() in ("yes", "true", "t", "1")
    elif target_type is int or target_type is float:
        return float(value)
    else:
        return value

def setup_networktables(ip=ip_address):
    global root_table, table_data, initialized_networktables
    if initialized_networktables:
        return
    NetworkTable.setIPAddress(ip)
    NetworkTable.setClientMode()
    NetworkTable.initialize()
    root_table = NetworkTable.getTable("")
    c_listener = ConnectionListener()
    root_table.addConnectionListener(c_listener)
    root_table.addGlobalListener(val_listener, True)
    initialized_networktables = True

@asyncio.coroutine
def networktables_websocket(request):
    # Setup websocket
    ws = web.WebSocketResponse()
    ws.start(request)

    # Setup connection dict
    con_id = len(connections)
    with table_data_lock:
        connection = {"socket": ws, "updated_data": True}
        connections.append(connection)
    print("NT Websocket {} Connected".format(con_id))

    # Start listener coroutine
    asyncio.async(networktables_websocket_listener(ws))

    # Set IP status data
    ip = request.transport.get_extra_info("sockname")[0]
    set_local_value("~SERVER_IP~", ip)

    last_data = dict()

    # Update periodically until the websocket is closed.
    try:
        while True:
            yield from asyncio.sleep(1)
            while True:
                yield from asyncio.sleep(.1)
                if connection["updated_data"]:
                    connection["updated_data"] = False
                    updates = dict_delta(last_data, table_data)
                    string_data = json.dumps(updates)
                    #print("Sending " + string_data)
                    ws.send_str(string_data)
                    last_data = deepcopy(table_data)
                if ws.closing:
                    break
            if ws.closing:
                break
    except weberrors.ClientDisconnectedError or weberrors.WSClientDisconnectedError:
        print("Client Disconnected")
    finally:
        print("NT Websocket {} Disconnected".format(con_id))
        with table_data_lock:
            connections.remove(connection)
        return ws

def dict_delta(dict_a, dict_b):
    """
    recursively compares two dictionaries, returns the dictionary of differences.
    aka retval = dict_b - dict_a
    """
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
    while True:
        try:
            jdata = yield from ws.receive_str()
            #print("Recieved " + jdata)
        except Exception:
            return
        data = json.loads(jdata)

        set_value(data["key"], data["value"])