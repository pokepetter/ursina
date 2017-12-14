import sys
sys.path.append("..")
from pandaeditor import *

class FirstPersonController(Entity):

    def __init__(self):
        super().__init__()
        self.model = 'cube_uv_top'
        self.texture = 'directions'
        self.scripts.append(self)

        self.speed = .1
        self.original_speed = self.speed

        world = Entity()
        world.parent = scene.render
        world.model = 'quad'
        world.texture = 'directions'
        world.rotation_x = 90
        world.scale = (20, 20, .1)
        world.color = color.lime

        cursor = load_prefab('panel')
        cursor.color = color.white
        cursor.scale *= .01
        cursor.rotation_z = 45


    def start(self):
        self.position = (0, 2, 1)
        camera.parent = self
        camera.position = (0,0,0)
        camera.rotation = (0,0,0)
        camera.fov = 90
        mouse.locked = True


    def update(self, dt):
        if scene.editor.enabled:
            return

        self.position += self.right * held_keys['d'] * self.speed
        self.position += self.forward * held_keys['w'] * self.speed
        self.position += self.left * held_keys['a'] * self.speed
        self.position += self.back * held_keys['s'] * self.speed

        self.rotation_y += mouse.velocity[0] * 20
        camera.rotation_x -= mouse.velocity[1] * 20
        camera.rotation_x = max(min(camera.rotation_x, 90), -90)
