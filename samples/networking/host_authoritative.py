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

# Used to show update positions from host without client side prediction.
shadow_box = Entity(model="quad", texture="white_cube", color=color.orange, parent=camera.ui, scale=0.1, y=0.1, z=0.1)

input_state = InputState()
other_input_state = InputState()

inputs_received = deque()
input_buffer = []
send_input_buffer = []

tick_rate = 1.0 / 60.0
tick_timer = 0.0
time_factor = 1.0

update_rate = 1.0 / 20.0
update_timer = 0.0

lerp_time = update_rate * 1.25
lerp_timer = 0.0

input_timer = 0.0

peer = RPCPeer()
peer.register_type(InputState, serialize_input_state, deserialize_input_state)

@rpc(peer)
def set_positions(connection, time_received, my_position: Vec2, other_position: Vec2, sequence_number: int):
    global lerp_timer, time_factor

    if connection.peer.is_hosting():
        return

    # Interpolate other entities (in this case only one).
    other_box.x = other_box.new_x
    other_box.y = other_box.new_y
    other_box.prev_x = other_box.x
    other_box.prev_y = other_box.y
    other_box.new_x = other_position.x
    other_box.new_y = other_position.y
    lerp_timer = 0.0

    sequence_delta = input_state.sequence_number - sequence_number

    # Maybe slow down if ahead of host.
    max_delta = ((update_rate / tick_rate) + 1) * 2
    if sequence_delta > max_delta:
        time_factor = 0.95
    elif sequence_delta < max_delta * 0.75:
        time_factor = 1.0

    # Reconcile with host.
    box.x = my_position.x
    box.y = my_position.y
    shadow_box.x = box.x
    shadow_box.y = box.y
    if sequence_delta > 0 and sequence_delta < len(input_buffer):
        # Re-apply all inputs after the last processed input.
        for state in input_buffer[len(input_buffer) - sequence_delta:]:
            box.x += float(int(state.right) - int(state.left)) * box_speed * tick_rate
            box.y += float(int(state.up) - int(state.down)) * box_speed * tick_rate


@rpc(peer)
def set_inputs(connection, time_received, input_states: list[InputState]):
    if not connection.peer.is_hosting():
        return

    if len(inputs_received) > 100:
        # Host is being spammed, disconnect.
        print("Peer is spamming inputs, disconnecting...")
        connection.disconnect()

    for state in input_states:
        inputs_received.append(state)

def tick(dt):
    global last_input_sequence_number_processed

    if time_factor < 1.0:
        print("Host is lagging, slowing down local simulation.")

    input_state.up = bool(held_keys["w"])
    input_state.down = bool(held_keys["s"])
    input_state.right = bool(held_keys["d"])
    input_state.left = bool(held_keys["a"])
    box.x += float(int(input_state.right) - int(input_state.left)) * box_speed * dt
    box.y += float(int(input_state.up) - int(input_state.down)) * box_speed * dt

    if not peer.is_hosting():
        input_state.sequence_number += 1
        input_buffer.append(input_state.copy())
        if len(input_buffer) >= 100:
            input_buffer.pop(0)
        send_input_buffer.append(input_buffer[-1])
        if len(send_input_buffer) > 10:
            send_input_buffer.pop(0)
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
        other_box.x += float(int(other_input_state.right) - int(other_input_state.left)) * box_speed * dt
        other_box.y += float(int(other_input_state.up) - int(other_input_state.down)) * box_speed * dt

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

    if peer.is_hosting():
        status_text.text = "Hosting on localhost, port 8080.\nWASD to move."
    else:
        status_text.text = "Connected to host with address localhost, port 8080.\nWASD to move."

    tick_timer += time.dt * time_factor
    while tick_timer >= tick_rate:
        tick(tick_rate)
        tick_timer -= tick_rate

    if not peer.is_hosting():
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
                peer.set_positions(
                    peer.get_connections()[0],
                    Vec2(other_box.x, other_box.y),
                    Vec2(box.x, box.y),
                    other_input_state.sequence_number
                )
            else:
                peer.set_inputs(peer.get_connections()[0], send_input_buffer)
                send_input_buffer.clear()
        update_timer = 0.0

def input(key):
    if key == "h":
        box.y = 0.1
        other_box.y = -0.1
        other_box.new_x = other_box.x
        other_box.new_y = other_box.y
        other_box.prev_x = other_box.x
        other_box.prev_y = other_box.y
        shadow_box.visible = False

        peer.start("localhost", 8080, is_host=True)
    elif key == "c":
        box.y = -0.1
        other_box.y = 0.1
        other_box.new_x = other_box.x
        other_box.new_y = other_box.y
        other_box.prev_x = other_box.x
        other_box.prev_y = other_box.y
        shadow_box.visible = True

        peer.start("localhost", 8080, is_host=False)

app.run()
