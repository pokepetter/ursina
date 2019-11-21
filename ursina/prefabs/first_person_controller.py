from ursina import *


class FirstPersonController(Entity):

    def __init__(self, **kwargs):
        super().__init__()
        self.speed = 5

        self.i = 0
        self.update_interval = 30

        self.cursor = Entity(
            parent = camera.ui,
            model = 'quad',
            color = color.pink,
            scale = .008,
            rotation_z = 45
            )

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
        self.position = (0, 1, 1)
        camera.rotation = (0,0,0)
        camera.position = (0,1.5,0)
        camera.fov = 90
        mouse.locked = True


        for key, value in kwargs.items():
            setattr(self, key ,value)


    def update(self):
        if self.i < self.update_interval:
            self.i += 1
            return

        self.direction = (
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            )

        if not raycast(self.world_position + self.up, self.direction, .5).hit:
            self.position += self.direction * self.speed * time.dt

        self.rotation_y += mouse.velocity[0] * 40
        camera.rotation_x -= mouse.velocity[1] * 40
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)

        self.y += held_keys['e']
        self.y -= held_keys['q']


if __name__ == '__main__':
    app = Ursina()
    Sky()
    Entity(model='plane', scale=100, color=color.yellow.tint(-.2), texture='white_cube', texture_scale=(100,100))
    FirstPersonController()
    app.run()
