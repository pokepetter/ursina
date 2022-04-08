from ursina import *

class NoclipMode:
    def __init__(self, speed=10, require_key='shift'):
        self.speed = speed
        self.require_key = require_key
        self.ignore_paused = True


    def input(self, key):
        if key == 'shift':
            # turn of entity's update and input functions
            if hasattr(self.entity, 'update'):
                self._entity_original_update = self.entity.update
                self.entity.update = None
            if hasattr(self.entity, 'input'):
                self._entity_original_input = self.entity.input
                self.entity.input = None

        if key == 'shift up':
            # assign them back again
            if hasattr(self.entity, 'update'):
                self.entity.update = self._entity_original_update
            if hasattr(self.entity, 'input'):
                self.entity.input = self._entity_original_input


    def update(self):
        if hasattr(window, 'exit_button'):
            window.exit_button.ignore = held_keys[self.require_key]

        if not held_keys[self.require_key]:
            return

        self.entity.y += (held_keys['e'] - held_keys['q']) * time.dt * self.speed

        direction = Vec3(
            self.entity.forward * (held_keys['w'] - held_keys['s'])
            + self.entity.right * (held_keys['d'] - held_keys['a'])
            ).normalized()

        self.entity.position += direction * time.dt * self.speed


class NoclipMode2d:
    def __init__(self, speed=10, require_key='shift'):
        self.speed = speed
        self.require_key = require_key
        self.ignore_paused = True


    def input(self, key):
        if key == 'shift':
            # turn of entity's update and input functions
            if hasattr(self.entity, 'update'):
                self._entity_original_update = self.entity.update
                self.entity.update = None
            if hasattr(self.entity, 'input'):
                self._entity_original_input = self.entity.input
                self.entity.input = None

        if key == 'shift up':
            # assign them back again
            if hasattr(self.entity, 'update'):
                self.entity.update = self._entity_original_update
            if hasattr(self.entity, 'input'):
                self.entity.input = self._entity_original_input


    def update(self):
        if hasattr(window, 'exit_button'):
            window.exit_button.ignore = held_keys[self.require_key]

        if not held_keys[self.require_key]:
            return

        self.entity.x += (held_keys['d'] - held_keys['a']) * time.dt * self.speed
        self.entity.y += (held_keys['w'] - held_keys['s']) * time.dt * self.speed




if __name__ == '__main__':
    app = Ursina()

    player = Entity(model='cube', color=color.orange)
    Entity(model='plane', scale=10)
    EditorCamera()
    # def update():
    #     player.x += held_keys['d'] * .1
    #     player.x -= held_keys['a'] * .1


    player.add_script(NoclipMode2d())
    app.run()
