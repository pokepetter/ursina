from ursina import *
from ursina.networking import *

app = Ursina(borderless=False)

start_text = "Press H to host or C to connect."
status_text = Text(text=start_text, origin=(0, 0))
messages = []

peer = Peer()

def on_connect(connection, time_connected):
    print("Connected to", connection.address)

def on_disconnect(connection, time_disconnected):
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

    if not peer.is_running():
        status_text.text = start_text
        return
    
    if peer.is_hosting():
        status_text.text = "Hosting on localhost, port 8080.\nSpace to send message."
    else:
        status_text.text = "Connected to host with address localhost, port 8080.\nSpace to send message."

def input(key):
    if key == "space":
        if peer.is_running():
            peer.send(peer.get_connections()[0], "Hello, World!".encode("utf-8"))
    elif key == "h":
        peer.start("localhost", 8080, is_host=True)
    elif key == "c":
        peer.start("localhost", 8080, is_host=False)

app.run()
 
