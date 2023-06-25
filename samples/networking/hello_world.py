from ursina import *
from ursina.networking import *

app = Ursina(size=(800, 600), borderless=False)

status_text = Text(text="Press H to host or C to connect.", origin=(0, 0))
messages = []

peer = Peer()

def on_connect(connection):
    print("Connected to", connection.address)

def on_disconnect(connection):
    print("Disconnected from", connection.address)

def on_data(connection, data, time_received):
    message = Text(text="Received: {}".format(data.decode("utf-8")), origin=(0, 0), y=-0.05-len(messages)*0.05)
    messages.append(message)
    s = Sequence(1, Func(message.fade_out, duration=0.5), 0.5, Func(destroy, message), Func(messages.pop, 0))
    s.start()

peer.on_connect = on_connect
peer.on_disconnect = on_disconnect
peer.on_data = on_data

def update():
    peer.update()

def input(key):
    if key == "space":
        if peer.is_running():
            peer.send(peer.get_connections()[0], "Hello, World!".encode("utf-8"))
    elif key == "h":
        peer.start("localhost", 8080, is_host=True)
        if peer.is_running():
            status_text.text = "Hosting on localhost, port 8080.\nSpace to send message."
    elif key == "c":
        peer.start("localhost", 8080, is_host=False)
        if peer.is_running():
            status_text.text = "Connected to host with address localhost, port 8080.\nSpace to send meesage."

app.run()
 
