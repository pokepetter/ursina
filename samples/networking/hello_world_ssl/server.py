from ursina import *
from ursina.networking import *

app = Ursina(size=(800, 600), borderless=False, window_type="none")

server = TCPPacketServer(path_to_certchain="./cert.pem", path_to_private_key="./key.pem")

def on_connect(connection):
    print("Connected to", connection.address)

def on_disconnect(connection):
    print("Disconnected from", connection.address)

def on_data(connection, data):
    print("Received:", str(data))

server.on_connect = on_connect
server.on_disconnect = on_disconnect
server.on_data = on_data

server.start("localhost", 8080)

def update():
    server.update()

app.run()
 
