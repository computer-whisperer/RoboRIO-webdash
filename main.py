#/usr/bin/python3
import asyncio
import netconsole_controller
from aiohttp import web

from os.path import abspath, dirname, join

ENABLE_NETWORKTABLES = True

ENABLE_NETCONSOLE = True

ENABLE_LIVEWINDOW = True

if ENABLE_NETWORKTABLES:
    try:
        import networktables
    except ImportError:
        ENABLE_NETWORKTABLES = False

if ENABLE_NETCONSOLE:
    try:
        import netconsole
    except ImportError:
        ENABLE_NETCONSOLE = False

@asyncio.coroutine
def data(request):
    return web.Response(body=b"Hello, world")

@asyncio.coroutine
def forward_request(request):
    return web.HTTPFound("/index.html")

def main():
    file_root = join(abspath(dirname(__file__)), "resources")

    app = web.Application()
    app.router.add_route("GET", "/netconsole", netconsole_controller.netconsole_websocket)
    app.router.add_route("GET", "/", forward_request)
    app.router.add_static("/", file_root)

    addr = ('127.0.0.1', 8400)

    loop = asyncio.get_event_loop()
    f = loop.create_server(app.make_handler(), port=8400)
    srv = loop.run_until_complete(f)
    print("Listening on http://%s:%s" % addr)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()