from ursina import *


class PlayerController(Entity):

    def __init__(self, **kwargs):
        super().__init__()
        self.speed = 5
        self.model='sphere'
        self.color =color.orange


    def update(self):
        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()

        ray = spherecast(self.world_position + self.up + (self.direction/2), radius=.5, debug=True)

        if not ray.hit:
            self.position += self.direction * self.speed * time.dt


if __name__ == '__main__':
    app = Ursina()

    Entity(model='cube', color=color.azure, collider='box', x=2, scale_z=2, scale_y=3)
    Entity(model='cube', color=color.azure, collider='box', z=2, scale_x=2, scale_y=3)
    Entity(model='cube', color=color.azure, collider='box', x=1, z=1, scale_x=2, scale_y=3, rotation_y=35)

    camera.position=(0,10,0)
    camera.orthographic = True
    camera.fov = 10
    camera.look_at((0,0,0))
    PlayerController()
    app.run()
