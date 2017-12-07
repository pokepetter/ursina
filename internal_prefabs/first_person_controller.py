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


    def start(self):
        self.position = (0, 2, 1)
        camera.parent = self
        camera.position = (0,0,0)
        camera.rotation = (0,0,0)
        camera.fov = 90
        mouse.locked = True


    def input(self, key):
        if key == 'w':
            self.w = True
        elif key == 'w up':
            self.w = False
        if key == 's':
            self.s = True
        elif key == 's up':
            self.s = False
        if key == 'd':
            self.d = True
        elif key == 'd up':
            self.d = False
        if key == 'a':
            self.a = True
        elif key == 'a up':
            self.a = False


    def update(self, dt):
        if scene.editor.enabled:
            return
        if self.w:
            self.position += self.forward * self.speed
        if self.s:
            self.position += self.back * self.speed
        if self.d:
            self.position += self.right * self.speed
        if self.a:
            self.position += self.left * self.speed

        self.rotation_y += mouse.velocity[0] * 20
        camera.rotation_x -= mouse.velocity[1] * 20
        camera.rotation_x = max(min(camera.rotation_x, 90), -90)
