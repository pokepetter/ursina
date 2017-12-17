import sys
sys.path.append("..")
from pandaeditor import *


class MinecraftClone(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'minecraft_clone'
        e = Entity()
        e.model = 'cube'
        cube = e.model
        voxel_parent = Entity()

        for z in range(32):
            for x in range(32):
                for y in range(1):
                    voxel = Voxel()
                    voxel.parent = voxel_parent
                    voxel.position = (x, y, z)

        player = FirstPersonController()
        player.parent = self

        # self.flattenStrong()


class Voxel(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'voxel'
        self.model = 'cube'
        self.origin = (0, .5, 0)
        self.collider = 'box'
        # self.texture = 'white_cube'
        self.color = color.random_color()


    def input(self, key):
        if self.hovered:
            if key == 'left mouse down' and self.hovered:
                voxel = Voxel()
                voxel.parent = self.parent
                voxel.position = self.position + mouse.normal

            if key == 'right mouse down':
                destroy(self)


class FirstPersonController(Entity):

    def __init__(self):
        super().__init__()
        self.speed = .1

        cursor = load_prefab('panel')
        cursor.color = color.dark_gray
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
        self.position += self.right * held_keys['d'] * self.speed
        self.position += self.forward * held_keys['w'] * self.speed
        self.position += self.left * held_keys['a'] * self.speed
        self.position += self.back * held_keys['s'] * self.speed

        self.rotation_y += mouse.velocity[0] * 20
        camera.rotation_x -= mouse.velocity[1] * 20
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)
