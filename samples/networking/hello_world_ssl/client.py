from ursina import *
from ursina.networking import *

app = Ursina(size=(800, 600), borderless=False)

client = TCPPacketClient(use_tls=True, path_to_cabundle="./cert.pem")

def on_connect(connection):
    print("Connected to", connection.address)

def on_disconnect(connection):
    print("Disconnected from", connection.address)

def on_data(connection, data):
    print("Received:", str(data))

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_data = on_data

def update():
    if not client.is_running():
        client.start("localhost", 8080)
    else:
        client.update()

def input(key):
    if key == "space":
        if client.is_running():
            print("Sending message...")
            client.send("Hello, World!".encode())

app.run()
