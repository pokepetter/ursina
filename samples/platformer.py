from ursina import *

class Player(Entity):
    def __init__(self):
        super().__init__()

        self.model = 'cube'
        self.origin = (0, -.5)
        self.scale = Vec2(1, 2)
        self.color = color.black

        self.walk_speed = .2
        self.jump_height = 2
        self.jump_duration = .6
        self.jumping = False
        self.max_jumps = 1
        self.jumps_left = self.max_jumps
        self.fall_speed = .002
        self.frames_skipped = 0
        self.fall_acceleration = 2.1 * 2
        self.air_time = 0
        self.y = raycast(self.world_position, self.down).point[1]


    def update(self):
        if held_keys['d']:
            self.x += self.walk_speed
        if held_keys['a']:
            self.x -= self.walk_speed

        camera.x = lerp(camera.x, self.x, 1/60 * 5)
        camera.y = lerp(camera.y, self.y, 1/60 * 5)
        camera.x = clamp(camera.x, 0, 20)


        ray = raycast(self.world_position, self.down)
        if ray.distance > .01 and not self.jumping: # not on ground and not on way up in jump
            self.y -= min(self.air_time, ray.distance)
            self.air_time += 1/30

            if raycast(self.world_position, self.down, .01).hit:
                # print('land')
                self.air_time = 0
                self.jumps_left = self.max_jumps

        elif held_keys['space']:
            invoke(self.jump, delay=.1)


    def input(self, key):
        if key == 'space':
            self.jump()

    def jump(self):
        if raycast(self.world_position, self.down).distance < .01:
            # print('jump')
            if hasattr(self, 'y_animator'):
                self.y_animator.pause()
            self.jump_dust = Entity(
                model = 'quad',
                scale = (.8, .8),
                color = color.red,
                position = self.position,
                origin = (0, -.5)
                )
            self.jump_dust.animate_scale((0,0,0), 2)
            destroy(self.jump_dust, 2.1)

            self.jumping = True
            self.jumps_left -= 1
            self.y += self.jump_height
            self.animate_y(self.y + self.jump_height, self.jump_duration, resolution=60, curve='ease_out_expo')
            invoke(self.fall, delay=self.jump_duration - .2)


    def fall(self):
        self.y_animator.pause()
        self.jumping = False


app = Ursina()
compress_textures()
window.color = color.smoke
camera.rotation_x = -5
camera.z = -40
camera.orthographic = True
bg = Entity(
    model = 'quad',
    texture = 'bg',
    z = 10,
    scale = (20, 10, 1) * 5
    )

ground = Entity(
    model = 'cube',
    color = color.gray,
    z = -.1,
    y = -1,
    scale = (10, 1, 10),
    collider = 'box',
    collision = True
    )

limit_bottom = Entity(
    model = 'cube',
    color = color.magenta,
    z = -.1,
    y = -3,
    origin = (0, .5),
    scale = (50, 1, 10),
    collider = 'box',
    collision = True
    )

player = Player()
app.run()
