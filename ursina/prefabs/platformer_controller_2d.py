from ursina import *


class PlatformerController2d(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.model = 'cube'
        self.origin_y = -.5
        self.scale_y = 2
        self.color = color.orange
        self.collider = 'box'

        self.animator = Animator({'idle' : None, 'walk' : None, 'jump' : None})
        # self.animation_state_machine.state = 'jump'
        # self.idle_animation = None
        # self.walk_animation = None
        # self.jump_animation = None
        # self.idle_animation = Entity(parent=self, model='cube', color=color.gray, origin_y=-.5, scale_z=2)
        # self.walk_animation = Animation(parent=self, texture='ursina_wink', color=color.red, origin_y=-.5, scale=(2,2), double_sided=True)
        # self.model = None

        self.walk_speed = 8
        self.walking = False
        self.velocity = 0
        self.jump_height = 4
        self.jump_duration = .5
        self.jumping = False
        self.max_jumps = 1
        self.jumps_left = self.max_jumps
        self.gravity = 1
        self.grounded = True
        self.air_time = 0

        self.y = 2
        ray = boxcast(self.world_position, self.down, distance=10, ignore=(self, ), thickness=1)
        if ray.hit:
            self.y = ray.world_point[1] + .01

        camera.add_script(SmoothFollow(target=self, offset=[0,1,-30], speed=4))

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._original_scale_x = self.scale_x


    def update(self):
        if raycast(self.position+Vec3(0,.05,0), self.right, .5, ignore=(self, ), debug=True).hit == False:
            self.x += self.velocity * time.dt * self.walk_speed

        self.walking = held_keys['a'] + held_keys['d'] > 0 and self.grounded

        # animations
        if not self.grounded:
            self.animator.state = 'jump'
        else:
            if self.walking:
                self.animator.state = 'walk'
            else:
                self.animator.state = 'idle'

        ray = boxcast(self.world_position+(0,.05,0), self.down, ignore=(self, ), thickness=.9)

        if ray.distance <= .1:
            if not self.grounded:
                self.land()
            self.grounded = True
            self.y = ray.world_point[1]
            return
        else:
            self.grounded = False

        # if not on ground and not on way up in jump, fall
        if not self.grounded and not self.jumping:
            self.y -= min(self.air_time, ray.distance-.05)
            self.air_time += time.dt*7



    def input(self, key):
        if key == 'space':
            self.jump()

        if key == 'd':
            self.velocity = 1
            self.scale_x = self._original_scale_x
        if key == 'd up':
            self.velocity = -held_keys['a']

        if key == 'a':
            self.velocity = -1
        if key == 'a up':
            self.velocity = held_keys['d']

        if held_keys['d'] or held_keys['a']:
            self.scale_x = self._original_scale_x * self.velocity


    def jump(self):
        if not self.grounded:
            return

        if hasattr(self, 'y_animator'):
            self.y_animator.pause()
        self.jump_dust = Entity(model=Circle(), scale=.5, color=color.white33, position=self.position)
        self.jump_dust.animate_scale(3, duration=.3, curve=curve.linear)
        self.jump_dust.fade_out(duration=.2)
        destroy(self.jump_dust, 2.1)

        self.jumping = True
        self.jumps_left -= 1
        self.grounded = False

        max_height = self.y + self.jump_height
        duration = self.jump_duration
        hit_above = boxcast(self.position+(0,.99,0), self.up, ignore=(self,), thickness=.9)
        if hit_above.hit:
            max_height = min(hit_above.distance-.5, max_height)
            duration *=  max_height / (self.y+self.jump_height)

        self.animate_y(max_height, duration, resolution=30, curve=curve.out_expo)
        invoke(self.start_fall, delay=duration)


    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False

    def land(self):
        # print('land')
        self.air_time = 0
        self.jumps_left = self.max_jumps
        self.grounded = True


if __name__ == '__main__':
    window.vsync = False
    app = Ursina()
    ground = Entity(model='cube', color=color.white33, origin_y=.5, scale=(20, 10, 1), collider='box')
    wall = Entity(model='cube', color=color.azure, origin=(-.5,.5), scale=(5,10), x=10, y=.5, collider='box')
    ceiling = Entity(model='cube', color=color.white33, origin_y=.5, scale=(10, 1, 1), y=5, collider='box')

    def input(key):
        if key == 'c':
            wall.collision = not wall.collision
            print(wall.collision)
            

    player_controller = PlatformerController2d()
    # EditorCamera()
    app.run()
