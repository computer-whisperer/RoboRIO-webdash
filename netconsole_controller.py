import asyncio
from aiohttp import web
import socket
import threading
import atexit
import sys
from queue import Queue, Empty

UDP_IN_PORT=6666
UDP_OUT_PORT=6668

@asyncio.coroutine
def netconsole_websocket(request):
    print("Doing something!")

    #Setup websocket
    ws = web.WebSocketResponse()
    ws.start(request)

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
            msg = sock_queue.get_nowait()

        except Empty:
            pass # no output

        else:
            #Send msg to the socket
            try:
                ws.send_str(str(msg, 'utf-8'))
            except web.WSClientDisconnectedError as exc:
                print(exc.code, exc.message)
                return ws

        yield from asyncio.sleep(0.05)