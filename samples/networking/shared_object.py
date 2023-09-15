from ursina import *
from ursina.networking import *

app = Ursina(borderless=False)

start_text = "Press H to host or C to connect."
status_text = Text(text=start_text, origin=(0, 0), z=1)

box = Entity(model="quad", texture="white_cube", color=color.red, parent=camera.ui, scale=0.1, y=0.1)
other_box = Entity(model="quad", texture="white_cube", color=color.blue, parent=camera.ui, scale=0.1, y=-0.1, z=0.5)
other_box.new_x = other_box.x
other_box.new_y = other_box.y
other_box.prev_x = other_box.x
other_box.prev_y = other_box.y

box_speed = 0.4

update_rate = 1.0 / 20.0
update_timer = 0.0

lerp_time = update_rate * 1.25
lerp_timer = 0.0

peer = RPCPeer()

@rpc(peer)
def set_position(connection, time_received, position: Vec2):
    global lerp_timer

    other_box.x = other_box.new_x
    other_box.y = other_box.new_y
    other_box.prev_x = other_box.x
    other_box.prev_y = other_box.y
    other_box.new_x = position.x
    other_box.new_y = position.y

    lerp_timer = 0.0

def update():
    global update_timer, lerp_timer 

    peer.update()
    if not peer.is_running():
        status_text.text = start_text
        box.x = 0.0
        box.y = 0.1
        other_box.x = 0.0
        other_box.y = -0.1
        return

    if peer.is_hosting():
        status_text.text = "Hosting on localhost, port 8080.\nWASD to move."
    else:
        status_text.text = "Connected to host with address localhost, port 8080.\nWASD to move."

    box.x += (held_keys["d"] - held_keys["a"]) * box_speed * time.dt
    box.y += (held_keys["w"] - held_keys["s"]) * box_speed * time.dt

    lerp_timer += time.dt
    other_box.x = lerp(other_box.prev_x, other_box.new_x, lerp_timer / lerp_time)
    other_box.y = lerp(other_box.prev_y, other_box.new_y, lerp_timer / lerp_time)
    if lerp_timer >= lerp_time:
        other_box.x = other_box.new_x
        other_box.y = other_box.new_y
        other_box.prev_x = other_box.x
        other_box.prev_y = other_box.y
        other_box.new_x = other_box.x
        other_box.new_y = other_box.y
        lerp_timer = 0.0

    update_timer += time.dt
    if update_timer >= update_rate:
        if peer.is_running() and peer.connection_count() > 0:
            peer.set_position(peer.get_connections()[0], Vec2(box.x, box.y))
        update_timer = 0.0

def input(key):
    if key == "h":
        box.y = 0.1
        other_box.y = -0.1
        other_box.new_x = other_box.x
        other_box.new_y = other_box.y
        other_box.prev_x = other_box.x
        other_box.prev_y = other_box.y

        peer.start("localhost", 8080, is_host=True)
    elif key == "c":
        box.y = -0.1
        other_box.y = 0.1
        other_box.new_x = other_box.x
        other_box.new_y = other_box.y
        other_box.prev_x = other_box.x
        other_box.prev_y = other_box.y

        peer.start("localhost", 8080, is_host=False)

app.run()
