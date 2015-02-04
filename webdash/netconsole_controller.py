import asyncio
from aiohttp import web, errors as weberrors
import socket
import threading
import atexit
import sys
import time
from queue import Queue, Empty

UDP_IN_PORT=6666
UDP_OUT_PORT=6668

received_logs = list()
log_update_limit = 50

@asyncio.coroutine
def netconsole_monitor():
    #set up receiving socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind( ('',UDP_IN_PORT) )

    #set up sending socket - use separate socket to avoid race condition
    out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    out.bind( ('',UDP_OUT_PORT) ) #bind is necessary for escoteric reasons stated on interwebs

    #set up atexit handler to close sockets
    def atexit_func():
        sock.close()
        out.close()

    atexit.register(atexit_func)

    #set up threads to emulate non-blocking io
    #thread-level emulation required for compatibility with windows
    stdin_queue = Queue()
    sock_queue = Queue()

    def enqueue_output_file(f, q):
        for line in iter(f.readline, b''): #thanks to stackoverflow
            q.put(line)

    def enqueue_output_sock(s, q):
        while True:
            q.put(s.recv(4096))

    stdin_reader = threading.Thread(target = enqueue_output_file, args = (sys.stdin, stdin_queue))
    sock_reader = threading.Thread(target = enqueue_output_sock, args = (sock, sock_queue))
    stdin_reader.daemon = True
    sock_reader.daemon = True
    stdin_reader.start()
    sock_reader.start()

    #main loop
    while True:
        try:
            msg = str(sock_queue.get_nowait(), 'utf-8')

        except Empty:
            pass # no output

        else:
            #Send msg to the socket
            try:
                process_log(msg)
            except web.WSClientDisconnectedError as exc:
                print(exc.code, exc.message)
                return
        yield from asyncio.sleep(0.05)

def process_log(message):
    log_data = {"message": message, "timestamp": time.monotonic()}
    received_logs.append(log_data)
    for websocket in websocket_connections[:]:
        try:
            websocket.send_str(message)
        except weberrors.ClientDisconnectedError or weberrors.WSClientDisconnectedError:
            pass


websocket_connections = list()

@asyncio.coroutine
def netconsole_websocket(request):

    wc = web.WebSocketResponse()
    wc.start(request)
    wc_id = len(websocket_connections)
    websocket_connections.append(wc)
    print("NC Websocket {} Connected".format(wc_id))
    yield from netconsole_websocket_listener(wc)
    print("NC Websocket {} Disonnected".format(wc_id))
    return wc

@asyncio.coroutine
def netconsole_websocket_listener(ws):
    while True:
        try:
            data = yield from ws.receive_str()
        except Exception:
            websocket_connections.remove(ws)
            return
        print(data)

@asyncio.coroutine
def netconsole_log_dump(request):
    print("Dumping logs to request.")
    data = "\n".join(l["message"] for l in received_logs)
    return web.Response(body=data.encode('utf-8'))