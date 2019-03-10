from ursina import *


class PlayerController(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.model = 'cube'
        self.origin_y = -.5
        self.scale_y = 2
        self.color = color.black
        self.collider = 'box'

        self.walk_speed = 8
        self.jump_height = 2
        self.jump_duration = .6
        self.jumping = False
        self.max_jumps = 1
        self.jumps_left = self.max_jumps
        # self.fall_speed = .002
        # self.fall_acceleration = 2.1 * 2
        self.air_time = 0
        self.y = raycast(self.world_position, self.down, ignore=(self, )).point[1]

        camera.add_script(SmoothFollow(target=self, offset=(0,1,-30), speed=4))

        for key, value in kwargs.items():
            setattr(self, key, value)


    def update(self):
        if raycast(self.position+Vec3(0,.5,0), self.right, .5, ignore=(self, ), debug=True).hit == False:
            self.x += held_keys['d'] * time.dt * self.walk_speed
        if raycast(self.position+Vec3(0,.5,0), self.left, .5, ignore=(self, ), debug=True).hit == False:
            self.x -= held_keys['a'] * time.dt * self.walk_speed

        ray = raycast(self.world_position, self.down, ignore=(self, ))
         # if not on ground and not on way up in jump, fall
        if not self.jumping and ray.distance > .01:
            self.y -= min(self.air_time, ray.distance)
            # make sure it doesn't overshoot into the collider
            if ray.hit and self.y < ray.point[1]:
                self.y = ray.point[1]

            self.air_time += 1/30

            if raycast(self.world_position, self.down, .01, ignore=(self, )).hit:
                # print('land')
                self.air_time = 0
                self.jumps_left = self.max_jumps


        elif held_keys['space']:
            invoke(self.jump, delay=.1)


    def input(self, key):
        if key == 'space':
            self.jump()

    def jump(self):
        hit = raycast(self.world_position, self.down, ignore=(self, ))
        if hit.distance < .01 and hit.distance < math.inf:
            print('jump', hit.distance)
            if hasattr(self, 'y_animator'):
                self.y_animator.pause()
            self.jump_dust = Entity(
                model = Circle(),
                scale = .5,
                color = color.white33,
                position = self.position,
                )
            self.jump_dust.animate_scale((3,3,3), duration=.3, curve='linear')
            self.jump_dust.fade_out(duration=.2)
            destroy(self.jump_dust, 2.1)

            self.jumping = True
            self.jumps_left -= 1
            self.y += self.jump_height
            self.animate_y(self.y + self.jump_height, self.jump_duration, resolution=60, curve='curve_out_expo')
            invoke(self.fall, delay=self.jump_duration - .2)


    def fall(self):
        self.y_animator.pause()
        self.jumping = False


if __name__ == '__main__':
    app = Ursina()
    ground = Entity(model = 'cube', color = color.lime,
        origin_y = .5, scale = (20, 10, 1), collider = 'box')

    wall = Entity(model='cube', color=color.azure, origin=(-.5,.5),
                scale=(5,10), x=10, y=.5, collider='box')
    player_controller = PlayerController()
    app.run()
