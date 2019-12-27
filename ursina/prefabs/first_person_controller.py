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


        self.position = (0, 1, 1)
        camera.rotation = (0,0,0)
        camera.fov = 90
        mouse.locked = True
        self.smooth_camera = False


        for key, value in kwargs.items():
            setattr(self, key ,value)


    def update(self):
        if self.i < self.update_interval:
            self.i += 1
            return

        self.rotation_y += mouse.velocity[0] * 40
        camera.rotation_x -= mouse.velocity[1] * 40
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)

        self.y += held_keys['e']
        self.y -= held_keys['q']

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()


        if not self.smooth_camera:
            camera.position = self.position + self.up*1.5
        else:
            camera.position = lerp(
                camera.position,
                self.position + (self.up*1.5),
                time.dt * 10)

        camera.rotation_y = self.rotation_y


        origin = self.world_position + self.up + (self.direction/2)
        middle_ray = raycast(origin , self.forward, ignore=[self,], distance=1.3, debug=False)
        left_ray =   raycast(origin, lerp(self.left, self.forward, .5), ignore=[self,], distance=1.4, debug=False)
        right_ray =   raycast(origin, lerp(self.right, self.forward, .5), ignore=[self,], distance=1.4, debug=False)

        self.smooth_camera = False

        # push away from the wall
        if left_ray.hit:
            self.smooth_camera = True
            self.position -= lerp(self.left, self.forward, .5) * (1.3-left_ray.distance)

        elif right_ray.hit:
            self.smooth_camera = True
            self.position -= lerp(self.right, self.forward, .5) * (1.3-right_ray.distance)



        if not middle_ray.hit:
            self.position += self.direction * self.speed * time.dt


if __name__ == '__main__':
    app = Ursina()
    Sky(color=color.gray)
    Entity(model='plane', scale=100, color=color.yellow.tint(-.2), texture='white_cube', texture_scale=(100,100))
    e = Entity(
        model='cube',
        scale=(1, 5, 10),
        x=2,
        y=.01,
        rotation_y = 45,
        collider='box',
        texture='white_cube',
    )
    e.texture_scale = (e.scale_z, e.scale_y)
    e = Entity(
        model='cube',
        scale=(1, 5, 10),
        x=-2,
        y=.01,
        collider='box',
        texture='white_cube',
    )
    e.texture_scale = (e.scale_z, e.scale_y)
    FirstPersonController()

    app.run()
