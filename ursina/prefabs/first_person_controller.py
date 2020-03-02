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

        self.position = (0, 1, 1)
        camera.position = self.position
        camera.rotation = (0,0,0)
        camera.fov = 90
        mouse.locked = True
        self.target_smoothing = 100
        self.smoothing = self.target_smoothing


        for key, value in kwargs.items():
            setattr(self, key ,value)


    def update(self):
        self.rotation_y += mouse.velocity[0] * 40
        camera.rotation_x -= mouse.velocity[1] * 40
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)

        self.y += held_keys['e']
        self.y -= held_keys['q']

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()


        self.smoothing = lerp(self.smoothing, self.target_smoothing, 4*time.dt)
        camera.position = lerp(
            camera.position,
            self.position + (self.up*1.5),
            self.smoothing / 100)

        camera.rotation_y = self.rotation_y

        origin = self.world_position + self.up + (self.direction/2)
        middle_ray = raycast(origin , self.direction, ignore=[self,], distance=1.3, debug=False)
        left_ray =   raycast(origin, lerp(self.left, self.forward, .5), ignore=[self,], distance=1.4, debug=False)
        right_ray =   raycast(origin, lerp(self.right, self.forward, .5), ignore=[self,], distance=1.4, debug=False)


        # push away from the wall
        if left_ray.hit:
            self.smoothing = 2
            self.position -= lerp(self.left, self.forward, .5) * (1.399-left_ray.distance)

        elif right_ray.hit:
            self.smoothing = 2
            self.position -= lerp(self.right, self.forward, .5) * (1.399-right_ray.distance)

        if not middle_ray.hit:
            self.position += self.direction * self.speed * time.dt


if __name__ == '__main__':
    app = Ursina()
    Sky(color=color.gray)
    ground = Entity(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='white_cube', texture_scale=(100,100), collider='box')
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
    player = FirstPersonController(y=1)

    def update():
        player.y -= 1* time.dt

        ray = raycast(player.position+player.up, player.down)
        if ray.hit:
            player.y = max(player.y, raycast(player.position+player.up, player.down).world_point[1])

    mouse.visible = True
    app.run()
