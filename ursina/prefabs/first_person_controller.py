from ursina import *


from panda3d.core import PStatClient

PStatClient.connect()


class Player(Entity):
    def __init__(self, ignore_entities = list(), **kwargs):
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
        super().__init__()
        self.speed = 5
        self.height = 2
        self.camera_pivot = Entity(parent=self, y=self.height)

        self.ignore_entities = ignore_entities
        self.ignore_entities.append(self)
        
        camera.parent = self.camera_pivot
        camera.position = (0,0,0)
        camera.rotation = (0,0,0)
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)
        self.collider='box'

        self.gravity = 9.8
        self.grounded = False
        self.jump_height = 2
        self.jump_up_duration = .5
        self.fall_after = .35 # will interrupt jump up
        self.jumping = False
        self.air_time = 0

        self.gravity_direction = Vec3(0, 1, 0)

        self.velocity = 0

        for key, value in kwargs.items():
            setattr(self, key ,value)

        # make sure we don't fall through the ground if we start inside it
        if self.gravity:
            ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=self.ignore_entities)
            if ray.hit:
                self.y = ray.world_point.y


    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()

        
        feet_ray = raycast(self.position+Vec3(0,.5,0), self.gravity_direction, ignore=self.ignore_entities, distance=1, debug=False)
        if not feet_ray.hit:
            self.velocity = 0
            move_amount = (self.direction - self.gravity_direction.normalized() + Vec3(0, self.scale.y, 0)) * time.dt * self.speed

            if raycast(self.position+Vec3(-.0,1,0), Vec3(1,0,0), distance=.5, ignore=self.ignore_entities).hit:
                move_amount[0] = min(move_amount[0], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(-1,0,0), distance=.5, ignore=self.ignore_entities).hit:
                move_amount[0] = max(move_amount[0], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,1), distance=.5, ignore=self.ignore_entities).hit:
                move_amount[2] = min(move_amount[2], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,-1), distance=.5, ignore=self.ignore_entities).hit:
                move_amount[2] = max(move_amount[2], 0)
            self.position += move_amount




            # self.position += self.direction * self.speed * time.dt


        if self.gravity:
            # gravity
            ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=self.ignore_entities)
            # ray = boxcast(self.world_position+(0,2,0), self.down, ignore=(self,))

            if ray.distance <= self.height+.1:
                if not self.grounded:
                    self.land()
                self.grounded = True
                # make sure it's not a wall and that the point is not too far up
                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5: # walk up slope
                    self.y = ray.world_point[1]
                return
            else:
                self.grounded = False

            # if not on ground and not on way up in jump, fall
            self.velocity += self.gravity * time.dt
            self.position -= min(self.air_time, ray.distance-.05) * self.gravity_direction / 3 * self.velocity * time.dt * 100
            self.air_time += time.dt * .25 * self.gravity


    def input(self, key):
        if key == 'space':
            self.jump()


    def jump(self):
        if not self.grounded:
            return

        self.grounded = False
        self.animate_y(self.y+self.jump_height, self.jump_up_duration, resolution=int(1//time.dt), curve=curve.out_expo)
        invoke(self.start_fall, delay=self.fall_after)


    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False

    def land(self):
        # print('land')
        self.air_time = 0
        self.grounded = True


    def on_enable(self):
        mouse.locked = True
        self.cursor.enabled = True


    def on_disable(self):
        mouse.locked = False
        self.cursor.enabled = False




class LightHouse(Entity):
    def __init__(self, player):
        super().__init__(
            model="blend/models/light house.obj",
            double_sided=True,
            position=(30, 2, 10),
            collider='mesh',
            enabled=False
        )
        
        self.player = player
        self.stairs_holder = Entity(
            model="cube", #blend/models/light house stairs holder.obj",
            collider="box",
            position=self.position,
            alpha=0.5
        )

        player.ignore_entities.append(self.stairs_holder)

        
    def update(self):
        if distance(self.player, self) < 10:
            if self.stairs_holder.intersects(self.player):
                print("Player Near")
                if held_keys["w"]:
                    self.player.y += 1 * time.dt





if __name__ == '__main__':
    from ursina.prefabs.first_person_controller import FirstPersonController
    window.vsync = False
    app = Ursina()
    # Sky(color=color.gray)
#    ground = Entity(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='white_cube', texture_scale=(100,100), collider='box')
    e = Entity(model='cube', scale=(1,5,10), x=2, y=.01, rotation_y=45, collider='box', texture='white_cube')
    e.texture_scale = (e.scale_z, e.scale_y)
    e = Entity(model='cube', scale=(1,5,10), x=-2, y=.01, collider='box', texture='white_cube')
    e.texture_scale = (e.scale_z, e.scale_y)

    player = Player(y=2, origin_y=-.5)
    player.gun = None

    ground = Entity(model=Terrain('terrain', skip=2), scale=(200, 3, 200), texture='grass.jpg', texture_scale=(50,50), y=-2)
    ground_collider = Entity(name="ground", model=Terrain('terrain', skip=8), scale=(200, 3, 200), collider = 'mesh', visible = False, y=-2)


    gun = Button(parent=scene, model='cube', color=color.blue, origin_y=-.5, position=(3,0,3), collider='box')
    gun.on_click = Sequence(Func(setattr, gun, 'parent', camera), Func(setattr, player, 'gun', gun))

    gun_2 = duplicate(gun, z=7, x=8)
    slope = Entity(model='cube', collider='box', position=(0,0,8), scale=6, rotation=(45,0,0), texture='brick', texture_scale=(8,8))
    slope = Entity(model='cube', collider='box', position=(5,0,10), scale=6, rotation=(80,0,0), texture='brick', texture_scale=(8,8))

    player.ignore_entities.append(slope)
    # hill = Entity(model='sphere', position=(20,-10,10), scale=(25,25,25), collider='sphere', color=color.green)
    # hill = Entity(model='sphere', position=(20,-0,10), scale=(25,25,25), collider='mesh', color=color.green)
    # from ursina.shaders import basic_lighting_shader
    # for e in scene.entities:
    #     e.shader = basic_lighting_shader

    hookshot_target = Button(parent=scene, model='cube', color=color.brown, position=(4,5,5))
    hookshot_target.on_click = Func(player.animate_position, hookshot_target.position, duration=.5, curve=curve.linear)


    LightHouse(player)
    player.y = 15
    
    def input(key):
        if key == 'left mouse down' and player.gun:
            gun.blink(color.orange)
            bullet = Entity(parent=gun, model='cube', scale=.1, color=color.black)
            bullet.world_parent = scene
            bullet.animate_position(bullet.position+(bullet.forward*50), curve=curve.linear, duration=1)
            destroy(bullet, delay=1)

        if key == 'q':
            mouse.locked = False

##            invoke(base.destroy, delay=.1)
##
##            import sys
##            invoke(sys.exit, delay=1)

    # player.add_script(NoclipMode())
    app.run()
