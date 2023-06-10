from ursina import *
from ursina.networking import *

app = Ursina(size=(800, 600), borderless=False, window_type="none")

server = RPCServer()

@rpc(server)
def echo(connection, msg: str):
    print(str(connection.address) + ":", msg)
    server.echo(connection, msg)

server.start("localhost", 8080)

def update():
    server.update()

app.run()
