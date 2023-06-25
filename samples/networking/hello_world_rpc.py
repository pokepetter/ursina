from ursina import *
from ursina.networking import *

app = Ursina(size=(800, 600), borderless=False)

status_text = Text(text="Press H to host or C to connect.", origin=(0, 0))
messages = []

peer = RPCPeer()

@rpc(peer)
def message(connection, time_received, msg: str):
    message = Text(text=f"Received: {msg}", origin=(0, 0), y=-0.05-len(messages)*0.05)
    messages.append(message)
    s = Sequence(1, Func(message.fade_out, duration=0.5), 0.5, Func(destroy, message), Func(messages.pop, 0))
    s.start()

def update():
    peer.update()

def input(key):
    if key == "space":
        if peer.is_running():
            peer.message(peer.get_connections()[0], "Hello, World!")
    elif key == "h":
        peer.start("localhost", 8080, is_host=True)
        if peer.is_running():
            status_text.text = "Hosting on localhost, port 8080.\nSpace to send message."
    elif key == "c":
        peer.start("localhost", 8080, is_host=False)
        if peer.is_running():
            status_text.text = "Connected to host with address localhost, port 8080.\nSpace to send meesage."

app.run()
 
