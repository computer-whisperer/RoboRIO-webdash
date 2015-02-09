#/usr/bin/python3
import asyncio
import sys
from os import symlink, remove
from os.path import abspath, dirname, join, exists

from aiohttp import web

from webdash import netconsole_controller
from webdash import networktables_controller

@asyncio.coroutine
def forward_request(request):
    return web.HTTPFound("/index.html")

INIT_FILE = "Webdash_init.sh"
INSTALL_LOCATIONS = "/etc/init.d/" + INIT_FILE, "/etc/rc5.d/S99" + INIT_FILE

def run_server(port):
    print("Starting Webdash Server.")
    file_root = join(abspath(dirname(__file__)), "resources")
    asyncio.async(netconsole_controller.netconsole_monitor())
    networktables_controller.setup_networktables()
    app = web.Application()
    app.router.add_route("GET", "/networktables", networktables_controller.networktables_websocket)
    app.router.add_route("GET", "/netconsole", netconsole_controller.netconsole_websocket)
    app.router.add_route("GET", "/netconsole_dump", netconsole_controller.netconsole_log_dump)
    app.router.add_route("GET", "/", forward_request)
    app.router.add_static("/", file_root)
    loop = asyncio.get_event_loop()
    f = loop.create_server(app.make_handler(), '0.0.0.0', port)
    srv = loop.run_until_complete(f)
    print("RoboRIO Webdash listening on", srv.sockets[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

def main():
    if len(sys.argv) <= 1:
        run_server(5801)
    elif sys.argv[1] == "install-initfile":
        for tgt in INSTALL_LOCATIONS:
            if not exists(dirname(tgt)):
                print("ERROR: Installation path {} does not exist. (Are you sure you are "
                      "installing this on an os with sysvinit?)".format(dirname(tgt)))
                exit(-1)
            src = join(abspath(dirname(__file__)), INIT_FILE)
            if exists(tgt):
                res = input("{} already exists, Remove? (y/N)".format(tgt))
                if res.lower() == "y":
                    remove(tgt)
                else:
                    print("ERROR: Target already exists.")
                    exit(-1)
            print("Symlinking {} to {}.".format(src, tgt))
            symlink(src, tgt)
            print("Successfully installed {}".format(INIT_FILE))
        exit(1)
    elif sys.argv[1] == "remove-initfile":
        for tgt in INSTALL_LOCATIONS:
            if not exists(tgt):
                print("ERROR: Init file {} not installed.".format(tgt))
            else:
                remove(tgt)
                print("Successfully removed {}".format(tgt))
        exit(1)
    else:
        if len(sys.argv) > 1:
            print("Unknown option: {}".format(sys.argv[1]))
        print("Usage: webdash [ , install-initfile, remove-initfile]")
        exit(1)

if __name__ == "__main__":
    main()