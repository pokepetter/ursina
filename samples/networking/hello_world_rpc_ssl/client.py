from ursina import *
from ursina.networking import *

app = Ursina(size=(800, 600), borderless=False)

client = RPCClient(use_tls=True, path_to_cabundle="./cert.pem")

@rpc(client)
def echo(connection, msg: str):
    print("Server echo:", msg)

def update():
    if not client.is_running():
        client.start("localhost", 8080)
    else:
        client.update()

def input(key):
    if key == "space":
        if client.is_running():
            client.echo("Hello, World!")

app.run()
 
