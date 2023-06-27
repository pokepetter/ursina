from ursina import *
from ursina.networking import *
from collections import deque

class InputState:
    def __init__(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.sequence_number = 0

    def copy(self):
        cpy = InputState()
        cpy.up = self.up
        cpy.down = self.down
        cpy.left = self.left
        cpy.right = self.right
        cpy.sequence_number = self.sequence_number
        return cpy

def serialize_input_state(writer, input_state):
    writer.write(input_state.up)
    writer.write(input_state.down)
    writer.write(input_state.left)
    writer.write(input_state.right)
    writer.write(input_state.sequence_number)

def deserialize_input_state(reader):
    input_state = InputState()
    input_state.up = reader.read(bool)
    input_state.down = reader.read(bool)
    input_state.left = reader.read(bool)
    input_state.right = reader.read(bool)
    input_state.sequence_number = reader.read(int)
    return input_state

app = Ursina(size=(800, 600), borderless=False)

start_text = "Press H to host or C to connect."
status_text = Text(text=start_text, origin=(0, 0), z=1)

box = Entity(model="quad", texture="white_cube", color=color.red, parent=camera.ui, scale=0.1, y=0.1)
other_box = Entity(model="quad", texture="white_cube", color=color.blue, parent=camera.ui, scale=0.1, y=-0.1, z=0.5)
other_box.new_x = other_box.x
other_box.new_y = other_box.y
other_box.prev_x = other_box.x
other_box.prev_y = other_box.y

box_speed = 0.4

input_state = InputState()
other_input_state = InputState()
input_buffer = []
inputs_received = deque()

tick_rate = 1.0 / 60.0
tick_timer = 0.0

update_rate = 1.0 / 20.0
update_timer = 0.0

lerp_time = update_rate * 1.25
lerp_timer = 0.0

input_timer = 0.0

peer = RPCPeer()
peer.register_type(InputState, serialize_input_state, deserialize_input_state)

@rpc(peer)
def set_positions(connection, time_received, my_position: Vec2, other_position: Vec2, sequence_number: int):
    global lerp_timer

    if connection.peer.is_hosting():
        return

    other_box.x = other_box.new_x
    other_box.y = other_box.new_y
    other_box.prev_x = other_box.x
    other_box.prev_y = other_box.y
    other_box.new_x = other_position.x
    other_box.new_y = other_position.y

    lerp_timer = 0.0

    box.x = position.x
    box.y = position.y

@rpc(peer)
def set_input(connection, time_received, input_states: list[InputState]):
    if not connection.peer.is_hosting():
        return

    for state in input_states:
        inputs_received.append(state)

def tick(dt):
    global last_input_sequence_number_processed

    input_state.up = bool(held_keys["w"])
    input_state.down = bool(held_keys["s"])
    input_state.right = bool(held_keys["d"])
    input_state.left = bool(held_keys["a"])

    if not peer.is_hosting():
        input_state.sequence_number += 1
        input_buffer.append(input_state.copy())
        if len(input_buffer) >= 100:
            input_buffer.pop(0)
    else:
        last_input_sequence_number_processed = other_input_state.sequence_number
        if len(inputs_received) > 0:
            state = inputs_received.popleft()
            other_input_state.up = state.up
            other_input_state.down = state.down
            other_input_state.left = state.left
            other_input_state.right = state.right
            other_input_state.sequence_number = state.sequence_number
        else:
            other_input_state.up = False
            other_input_state.down = False
            other_input_state.left = False
            other_input_state.right = False

def update():
    global update_timer, lerp_timer, tick_timer

    peer.update()
    if not peer.is_running():
        status_text.text = start_text
        box.x = 0.0
        box.y = 0.1
        other_box.x = 0.0
        other_box.y = -0.1
        return

    tick_timer += time.dt
    if tick_timer >= tick_rate:
        tick(tick_rate)
        tick_timer = 0.0

    box.x += float(int(input_state.right) - int(input_state.left)) * box_speed * time.dt
    box.y += float(int(input_state.up) - int(input_state.down)) * box_speed * time.dt
    if peer.is_hosting():
        other_box.x += float(int(other_input_state.right) - int(other_input_state.left)) * box_speed * time.dt
        other_box.y += float(int(other_input_state.up) - int(other_input_state.down)) * box_speed * time.dt
    else:
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
            if peer.is_hosting():
                peer.set_position(peer.get_connections()[0], Vec2(box.x, box.y))
            else:
                peer.set_input(peer.get_connections()[0], input_buffer)
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
        if peer.is_running():
            status_text.text = "Hosting on localhost, port 8080.\nWASD to move."
    elif key == "c":
        box.y = -0.1
        other_box.y = 0.1
        other_box.new_x = other_box.x
        other_box.new_y = other_box.y
        other_box.prev_x = other_box.x
        other_box.prev_y = other_box.y

        peer.start("localhost", 8080, is_host=False)
        if peer.is_running():
            status_text.text = "Connected to host with address localhost, port 8080.\nWASD to move."

app.run()
