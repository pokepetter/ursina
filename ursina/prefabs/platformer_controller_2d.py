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
        self.velocity = 0 # the walk diection is stored here. -1 for left and 1 for right.
        self.jump_height = 4
        self.jump_duration = .5
        self.jumping = False
        self.max_jumps = 1
        self.jumps_left = self.max_jumps
        self.gravity = 1
        self.grounded = True
        self.air_time = 0   # this increase while we're falling and used when calculating the distance we fall so we fall faster and faster instead of linearly.
        self.traverse_target = scene     # by default, it will collide with everything except itself. you can change this to change the boxcast traverse target.
        self._start_fall_sequence = None # we need to store this so we can interrupt the fall call if we try to double jump.

        ray = boxcast(self.world_position, self.down, distance=10, ignore=(self, ), traverse_target=self.traverse_target, thickness=.9)
        if ray.hit:
            self.y = ray.world_point[1] + .01
        # camera.add_script(SmoothFollow(target=self, offset=[0,1,-30], speed=4))

        for key, value in kwargs.items():
            setattr(self, key, value)

        # delay_gravity one frame
        target_gravity = self.gravity
        self.gravity = 0
        invoke(setattr, self, 'gravity', target_gravity, delay=1/60)
        self._original_scale_x = self.scale_x


    def update(self):
        # check in the direction we're walking to see if there's a wall. If it does not hit, move.
        if boxcast(
            self.position+Vec3(self.velocity * time.dt * self.walk_speed,self.scale_y/2,0),
            # self.position+Vec3(sefl,self.scale_y/2,0),
            direction=Vec3(self.velocity,0,0),
            distance=abs(self.scale_x/2),
            ignore=(self, ),
            traverse_target=self.traverse_target,
            thickness=(self.scale_x*.9, self.scale_y*.9),
            ).hit == False:

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


        # check if we're on the ground or not.
        ray = boxcast(
            self.world_position+Vec3(0,.1,0),
            self.down,
            distance=max(.1, self.air_time * self.gravity),
            ignore=(self, ),
            traverse_target=self.traverse_target,
            thickness=self.scale_x*.9
            )

        if ray.hit:
            if not self.grounded:
                self.land()
            self.grounded = True
            self.y = ray.world_point[1]
            return
        else:
            self.grounded = False

        # if not on ground and not on way up in jump, fall
        if not self.grounded and not self.jumping:
            self.y -= min(self.air_time * self.gravity, ray.distance-.1)
            self.air_time += time.dt*4 * self.gravity


        # if in jump and hit the ceiling, fall
        if self.jumping:
            if boxcast(self.position+(0,.1,0), self.up, distance=self.scale_y, thickness=.95, ignore=(self,), traverse_target=self.traverse_target).hit:
                self.y_animator.kill()
                self.air_time = 0
                self.start_fall()



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
        if not self.grounded and self.jumps_left <= 1:
            return

        if self._start_fall_sequence:
            self._start_fall_sequence.kill()

        # don't jump if there's a ceiling right above us
        if boxcast(self.position+(0,.1,0), self.up, distance=self.scale_y, thickness=.95, ignore=(self,), traverse_target=self.traverse_target).hit:
            return

        if hasattr(self, 'y_animator'):
            self.y_animator.kill()
        self.jump_dust = Entity(model=Circle(), scale=.5, color=color.white33, position=self.position)
        self.jump_dust.animate_scale(3, duration=.3, curve=curve.linear)
        self.jump_dust.fade_out(duration=.2)
        destroy(self.jump_dust, 2.1)

        self.jumping = True
        self.jumps_left -= 1
        self.grounded = False

        target_y = self.y + self.jump_height
        duration = self.jump_duration
        # check if we hit a ceiling and adjust the jump height accordingly
        hit_above = boxcast(self.position+(0,self.scale_y/2,0), self.up, distance=self.jump_height-(self.scale_y/2), thickness=.9, ignore=(self,))
        if hit_above.hit:
            target_y = min(hit_above.world_point.y-self.scale_y, target_y)
            # print('------', target_y)
            try:
                duration *= target_y / (self.y+self.jump_height)
            except ZeroDivisionError as e:
                return e

        self.animate_y(target_y, duration, resolution=30, curve=curve.out_expo)
        self._start_fall_sequence = invoke(self.start_fall, delay=duration)


    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False


    def land(self):
        # print('land')
        self.air_time = 0
        self.jumps_left = self.max_jumps
        self.grounded = True



if __name__ == '__main__':
    # window.vsync = False
    app = Ursina()
    camera.orthographic = True
    camera.fov = 10

    ground = Entity(model='cube', color=color.white33, origin_y=.5, scale=(20, 10, 1), collider='box')
    wall = Entity(model='cube', color=color.azure, origin=(-.5,.5), scale=(5,10), x=10, y=.5, collider='box')
    wall_2 = Entity(model='cube', color=color.white33, origin=(-.5,.5), scale=(5,10), x=10, y=5, collider='box')
    ceiling = Entity(model='cube', color=color.white33, origin_y=-.5, scale=(1, 1, 1), y=1, collider='box')

    def input(key):
        if key == 'c':
            wall.collision = not wall.collision
            print(wall.collision)


    player_controller = PlatformerController2d(scale_y=2, jump_height=4, x=3)
    camera.add_script(SmoothFollow(target=player_controller, offset=[0,1,-30], speed=4))

    EditorCamera()
    app.run()
