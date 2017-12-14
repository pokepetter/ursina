from pandaeditor import *

class MinecraftClone(Entity):

    def __init__(self):
        super().__init__()

        for z in range(10):
            for x in range(10):
                voxel = Voxel()
                voxel.parent = self
                voxel.position = (x, 0, z)

        player = FirstPersonController()
        player.parent = self


class Voxel(Entity):

    def __init__(self):
        super().__init__()
        self.model = 'cube'
        self.collider = 'box'
        self.texture = 'white_cube'
        self.scripts.append(self)

    def input(self, key):
        if key == 'left mouse down' and self.hovered:
            if keys.alt:
                destroy(self)
            else:
                voxel = load_prefab('voxel')
                voxel.parent = self.parent
                voxel.position = self.position + mouse.normal


class FirstPersonController(Entity):

    def __init__(self):
        super().__init__()
        self.scripts.append(self)
        self.speed = .1

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
        self.position += self.right * held_keys['d'] * self.speed
        self.position += self.forward * held_keys['w'] * self.speed
        self.position += self.left * held_keys['a'] * self.speed
        self.position += self.back * held_keys['s'] * self.speed

        self.rotation_y += mouse.velocity[0] * 20
        camera.rotation_x -= mouse.velocity[1] * 20
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)
