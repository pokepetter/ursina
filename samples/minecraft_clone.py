from ursina import *


class MinecraftClone(Entity):

    def __init__(self):
        super().__init__()

        for z in range(32):
            for x in range(32):
                for y in range(1):
                    voxel = Voxel()
                    voxel.name = 'voxel_' + str(x) + '_' + str(z)
                    voxel.parent = self
                    voxel.position = (x, y, z)

        sky = load_prefab('sky')

        player = FirstPersonController()
        player.parent = self


class Voxel(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'voxel'
        self.model = 'cube'
        self.collider = 'box'
        self.texture = 'white_cube'
        self.color = color.color(0, 0, random.uniform(.9, 1.0))
        # self.origin = (0, .5, 0)


    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                voxel = Voxel()
                voxel.parent = self.parent
                voxel.position = self.position + mouse.normal

            if key == 'right mouse down':
                destroy(self)


class FirstPersonController(Entity):

    def __init__(self):
        super().__init__()
        self.speed = .25

        self.i = 0
        self.update_interval = 30

        cursor = Panel()
        cursor.color = color.pink
        cursor.scale *= .008
        cursor.rotation_z = 45

        self.graphics = Entity(
            name = 'player_graphics',
            parent = self,
            model = 'cube',
            origin = (0, -.5, 0),
            scale = (1, 1.8, 1),
            )

        self.arrow = Entity(
            parent = self.graphics,
            model = 'cube',
            color = color.blue,
            position = (0, .5, .5),
            scale = (.1, .1, .5)
            )

        camera.parent = self
        self.position = (0, .5, 1)
        camera.rotation = (0,0,0)
        camera.position = (0,2,0)
        camera.fov = 90
        mouse.locked = True


    def update(self):
        if self.i < self.update_interval:
            self.i += 1
            return

        self.direction = (
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            )

        if not raycast(self.world_position + self.up, self.direction, 1).hit:
            self.position += self.direction * self.speed

        self.rotation_y += mouse.velocity[0] * 40
        camera.rotation_x -= mouse.velocity[1] * 40
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)


if __name__ == '__main__':
    app = Ursina()
    MinecraftClone()
    app.run()
