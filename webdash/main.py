#/usr/bin/python3
import asyncio
import sys
from os.path import abspath, dirname, join

from aiohttp import web

from webdash import netconsole_controller
from webdash import networktables_controller

@asyncio.coroutine
def forward_request(request):
    return web.HTTPFound("/index.html")

def main():
    if len(sys.argv) <= 1:
        file_root = join(abspath(dirname(__file__)), "resources")
        asyncio.async(netconsole_controller.netconsole_monitor())
        networktables_controller.setup_networktables()
        app = web.Application()
        app.router.add_route("GET", "/networktables", networktables_controller.networktables_websocket)
        app.router.add_route("GET", "/netconsole", netconsole_controller.netconsole_websocket)
        app.router.add_route("GET", "/netconsole_dump", netconsole_controller.netconsole_log_dump)
        app.router.add_route("GET", "/", forward_request)
        app.router.add_static("/", file_root)

        addr = ('127.0.0.1', 8410)

        loop = asyncio.get_event_loop()
        f = loop.create_server(app.make_handler(), port=8410)
        srv = loop.run_until_complete(f)
        print("Listening on http://%s:%s" % addr)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
    elif sys.argv[1] == "install-initfile":
        print("TODO!!!!")
        exit(1)

if __name__ == "__main__":
    main()