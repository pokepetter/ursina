# touch_input.py

from ursina import *
from ursina.prefabs.draggable import Draggable


# ———————————————————————————————————————
# On‑Screen Controls
# ———————————————————————————————————————

class VirtualJoystick(Entity):
    """An on-screen joystick for touch input."""
    def __init__(self, radius=80, position=(0,0), **kwargs):
        super().__init__(parent=camera.ui, position=position, scale=(.2, .2), **kwargs)
        # convert pixel radius to UI space
        self.radius = radius / 100
        self.bg = Entity(parent=self, model='circle', color=color.dark_gray, scale=2)
        self.knob = Draggable(parent=self, model='circle', color=color.white, scale=1)
        self.knob.always_on_top = True
        self.knob.start_position = self.knob.position
        self.value = Vec2(0,0)

    def update(self):
        if self.knob.dragging:
            # get 2D offset
            off = Vec2(self.knob.position.x, self.knob.position.y)
            # clamp to radius
            if off.length() > self.radius:
                off = off.normalized() * self.radius
            # reposition knob (preserve z)
            self.knob.position = Vec3(off.x, off.y, self.knob.position.z)
            # normalize −1..+1
            self.value = off / self.radius
        else:
            self.knob.position = self.knob.start_position
            self.value = Vec2(0,0)


class VirtualButton(Button):
    """An on-screen button that updates held_keys[key_name]."""
    def __init__(self, key_name, position=(0,0), color=color.azure, **kwargs):
        super().__init__(
            parent=camera.ui,
            model='circle',
            collider='box',
            position=position,
            color=color,
            scale=.1,
            **kwargs
        )
        self.key_name = key_name

    def on_press(self):
        held_keys[self.key_name] = 1
        invoke(lambda: input(self.key_name), delay=0)
        return True  # consume the event

    def on_release(self):
        held_keys[self.key_name] = 0
        invoke(lambda: input(f'{self.key_name} up'), delay=0)
        return True

    def input(self, key):
        # eat clicks so they don't pass to scene
        if key == 'left mouse down' and mouse.hovered_entity == self:
            return True


# ———————————————————————————————————————
# Unified InputHandler
# ———————————————————————————————————————

class InputHandler:
    """
    Unified input for desktop and touch:
      - get_movement_vector() -> Vec2(x:left/right, y:forward/back)
      - get_look_vector()     -> Vec2(x:turn,      y:look up/down)
      - is_action_pressed(name)
      - bind_action(name, key)
    """
    def __init__(self, use_touch=False):
        self.use_touch = use_touch
        self.joystick_move = None
        self.joystick_look = None
        self.virtual_buttons = {}
        self._action_map = {}

        if self.use_touch:
            self._setup_virtual_controls()

    def _setup_virtual_controls(self):
        # two joysticks
        self.joystick_move = VirtualJoystick(position=(-.7, -.3))
        self.joystick_look = VirtualJoystick(position=( .3, -.3))

        # Now include all four buttons
        self.virtual_buttons = {
            'a': VirtualButton('gamepad a', position=( .7, -.1), color=color.lime),
            'b': VirtualButton('gamepad b', position=( .8, -.2), color=color.red),
            'x': VirtualButton('gamepad x', position=( .6, -.2), color=color.cyan),
            'y': VirtualButton('gamepad y', position=( .7, -.3), color=color.yellow),
        }

        # default mapping: logical name -> held_keys key
        self._action_map = { name: btn.key_name for name, btn in self.virtual_buttons.items() }

    def update(self):
        """Call once per frame in your update() to refresh touch controls."""
        if self.use_touch:
            self.joystick_move.update()
            self.joystick_look.update()

    def get_movement_vector(self):
        """Vec2: (-1..1, -1..1) movement axis."""
        if self.use_touch and self.joystick_move:
            return Vec2(self.joystick_move.value)
        # WASD fallback
        return Vec2(held_keys['d'] - held_keys['a'],
                    held_keys['w'] - held_keys['s'])

    def get_look_vector(self):
        """Vec2: (turn, pitch) axis."""
        if self.use_touch and self.joystick_look:
            return Vec2(self.joystick_look.value)
        # mouse fallback
        return Vec2(mouse.velocity[0], -mouse.velocity[1])

    def is_action_pressed(self, action_name):
        """True if the mapped key for this action is down."""
        key = self._action_map.get(action_name)
        return held_keys[key] if key else False

    def bind_action(self, action_name, key_name):
        """
        Dynamically rebind an action to a different key.
        If use_touch=True and action_name exists, updates that button too.
        """
        self._action_map[action_name] = key_name
        if self.use_touch and action_name in self.virtual_buttons:
            self.virtual_buttons[action_name].key_name = key_name


# ———————————————————————————————————————
# Usage Example (append under your main app)
# ———————————————————————————————————————

if __name__ == '__main__':
    app = Ursina()
    window.vsync = False

    # On-screen controls + mapping
    handler = InputHandler(use_touch=True)
    print(type(handler.virtual_buttons))

    # Example: you can ignore the handler and just grab the joysticks/buttons directly:
    joystick_left   = handler.joystick_move
    joystick_right  = handler.joystick_look
    btn_list        = handler.virtual_buttons.values()   # a list-like view of buttons

    # Game world setup
    player     = Entity(model='cube', color=color.orange, scale=1.2)
    Text.default_resolution = 1080 * Text.size
    debug_text = Text(x=-.5, y=.4, origin=(0,0), color=color.black)

    # Common handler for button presses
    def handle_input(key):
        if key == 'gamepad a':
            player.animate_y(player.y + .5, duration=.2, curve=curve.out_bounce)
        elif key == 'gamepad b':
            player.position += player.forward.normalized() * 1
        elif key == 'gamepad x':
            player.color = color.random_color()
        elif key == 'gamepad y':
            factor = 2 if player.scale_x < 1.5 else 0.5
            player.animate_scale(player.scale * factor, duration=.2)

    # bind all on-screen buttons to handle_input
    for btn in btn_list:
        btn.on_click = lambda key=btn.key_name: handle_input(key)

    Sky()

    def update():
        handler.update()

        # Movement
        move_x = joystick_left.value.x * time.dt * 4
        move_z = joystick_left.value.y * time.dt * 4
        player.position += player.right * move_x + player.forward * move_z

        # Rotation
        rot_y = joystick_right.value.x * time.dt * 100
        rot_x = -joystick_right.value.y * time.dt * 50
        player.rotation_y += rot_y
        player.rotation_x += rot_x  

        debug_text.text = (
            f"LStick: {joystick_left.value}\n"
            f"RStick: {joystick_right.value}\n"
            f"Pos: {player.position}, Rot: {player.rotation}"
        )

    app.run()