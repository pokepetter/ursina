from ursina import *
from ursina.scripts.property_generator import generate_properties_for_class
from ursina.shaders.unlit_shader import unlit_shader
from ursina.shaders.matcap_shader import matcap_shader
import shutil


cache = dict()
# If a name and seed is provided, it will replay the instance if it exists.
# This will be faster to play since you only have to instantiate the paritcles and animations once.
# However, this means you can only have one instance playing at the same time.
# If the particle effect has been baked, it will instead load an FrameAnimation3D.

# Instead of dealing with metaclass mess, just use a function to determine whether we should return a new ParticleSystem, acached one, or a FrameAnimations3D(baked).
def ParticleSystem(**kwargs):
    kwargs = _ParticleSystem.default_values | kwargs
    id = None
    if kwargs['name'] and kwargs['seed'] is not None:
        id = f'{kwargs['name']}_{kwargs['seed']}'
        # print('id:', id, f'{id}_0000', load_model(f'{id}_0000'))

        if kwargs['use_cache'] and load_model(f'{id}_0000'): # if the particle system has been baked, return a FrameAnimation3D
            # print('return particled baked to FrameAnimation3d', id)
            kwargs |= {'name':f'{id}_', 'fps':30, 'loop':False}
            instance = FrameAnimation3d(**kwargs)
            return instance

        if kwargs['use_cache'] and id in cache:
            cache[id].position = kwargs.get('position', Vec3.zero)
            cache[id].auto_destroy = False
            cache[id].play()
            # print('return cached', id)
            return cache[id]

    instance = _ParticleSystem(**kwargs)
    if id and kwargs['use_cache']:
        cache[id] = instance
        # print('add to cache:', id)

    return instance


@generate_properties_for_class()
class _ParticleSystem(Entity):
    default_values = dict(
        start_size=1,
        end_size=0,
        size_curve=curve.in_expo,
        color_curve=curve.in_expo,

        start_color=color.white,
        end_color=color.white,

        start_direction=Vec3(0,0,0),
        direction_randomness=Vec3(0,0,0),
        start_rotation=Vec3(0,0,0),
        rotation_randomness=Vec3(0,0,0),    # rotates the model only, not the direction it moves in
        spin=Vec3(0,0,0),
        spin_curve = curve.linear,

        auto_play=True,
        num_particles=1,   # if 0, will be set to the length of the spawn_points list
        speed=0,
        speed_curve=curve.linear,
        move_directions='forward',  # local forward

        bounce=0,
        bounce_curve=curve.out_bounce,

        max_particles=20,
        lifetime=1,
        mesh='quad',
        double_sided=True,

        world_space=False,
        shader=unlit_shader,
        texture=None,
        always_on_top=False,
        unlit=True,

        spawn_points=(Vec3.zero, ),
        spawn_type='burst', # 'burst', 'random' / 'sequential' / 'continious'
        loop_every=0,
        spawn_interval=0,     # only applies if spawn_type is random, sequential or continuous
        delay=0,

        auto_destroy=True,
        name='',    # if we give a name and a seed, cache the generated particle animation.
        seed=None,  # set which random seed to use. int / int tuple/list
        use_cache=True, # set to False to force making a new instance
    )

    def __init__(self, **kwargs):
        kwargs = __class__.default_values | kwargs
        super().__init__(**kwargs)

        if self.num_particles == 0:
            self.num_particles = len(self.spawn_points)

        if not isinstance(self.move_directions, (tuple, list)):
            self.move_directions = [self.move_directions for i in range(self.num_particles)]

        if not isinstance(self.start_color, (tuple, list)):
            self.start_color = (self.start_color, )
        if not isinstance(self.end_color, (tuple, list)):
            self.end_color = (self.end_color, )

        if not isinstance(self.speed, (tuple, list)):
            self.speed = (self.speed, self.speed)

        self.spawn_points = LoopingList(self.spawn_points)
        self.particles = []
        self.t = 0
        self.total_duration = self.lifetime + (self.num_particles * self.spawn_interval)
        self.is_playing = False

        self.generate()
        if self.auto_play:
            invoke(self.play, delay=self.delay)


    def update(self):
        if self.loop_every == 0:
            return
        if self.is_playing:
            # print(self.t,)
            self.t += time.dt

        if self.t > self.loop_every:
            self.generate()
            self.play()
            self.t = 0


    def generate(self):
        self.anims = []

        if self.spawn_type == 'burst':
            [self.generate_particle_animations(position=Vec3.zero, move_direction=self.move_directions[i], delay=i*self.spawn_interval, i=i) for i in range(self.num_particles)]

        elif self.spawn_type == 'random':
            [self.generate_particle_animations(position=random.choice(self.spawn_points), move_direction=self.move_directions[i], delay=i*self.spawn_interval, i=i) for i in range(self.num_particles)]

        elif self.spawn_type == 'sequential':
            [self.generate_particle_animations(position=self.spawn_points[i], move_direction=self.move_directions[i], delay=i*self.spawn_interval, i=i) for i in range(self.num_particles)]


    def play(self):
        self.t = 0
        for e in self.anims:
            e.start()
        self.is_playing = True


    def bake(self, fps=30):
        if not self.name:
            raise Exception(f'can not bake, {self} has no name')

        if self.seed is None:
            raise Exception(f'can not bake, {self} has no seed')

        if not self.anims:
            self.generate()

        duration_per_frame = 1 / fps
        num_frames = int(self.total_duration / duration_per_frame)
        print('num_frames:', num_frames)

        folder = application.compressed_models_folder / self.name
        if folder.exists() and folder.is_dir():
            shutil.rmtree(folder)
        folder.mkdir(parents=True, exist_ok=True)


        for i in range(num_frames):
            self.model = None
            if self.children:
                self.combine(auto_destroy=False)
            else:
                self.model = Mesh()

            self.model.save(f'{self.name}_{self.seed}_{str(i).zfill(4)}.bam', folder)
            for seq in self.anims:
                seq.t += 1/60
                seq.started = True
                seq.update()
                seq.started = False


    def generate_particle_animations(self, position, move_direction, delay=0, i=0):
        if self.seed is None:
            random.seed(self.seed)
        else:
            random.seed(self.seed+i)    # use seed + particle index so the particle system will be somewhat random, but prevent each particle from facing the same direction.

        if len(self.particles) >= self.max_particles:
            return

        model = self.mesh
        if not isinstance(model, str):
            model = copy(model)

        e = Entity(parent=self, scale=self.start_size, position=position, enabled=False)
        e.rotation = self.start_direction + Vec3(*[random.uniform(-e/2, e/2) for e in self.direction_randomness])
        if isinstance(move_direction, str):
            move_direction = getattr(e, move_direction).normalized()
            # e.look_at(e.position + direction)
        m = Entity(parent=e, model=model, origin=self.origin, double_sided=self.double_sided, shader=self.shader, texture=self.texture, always_on_top=self.always_on_top, unlit=self.unlit)
        m.rotation = self.start_rotation + Vec3(*[random.uniform(-e/2, e/2) for e in self.rotation_randomness])

        if self.world_space:
            e.world_parent = scene

        m.color = random.choice(self.start_color)
        should_destroy = False
        if not (self.use_cache and self.name and self.seed is not None) or self.loop_every > 0:
            should_destroy = True
            # print_on_screen('should_destroy:', should_destroy)


        self.anims.append(Sequence(
            Wait(delay),
            # Func(print, 'enable'),
            Func(self.try_enabling, e),
            Func(setattr, e, 'position', e.position),
            Func(setattr, e, 'rotation', e.rotation),
            Func(setattr, m, 'scale', m.scale),
            Func(setattr, m, 'color', m.color),
            Func(setattr, m, 'rotation', m.rotation),
            Func(setattr, m, 'y', m.y),
            started=False, auto_destroy=should_destroy, name='start_sequence'))
        self.anims.extend(e.animate_position(e.position + (move_direction * random.uniform(self.speed[0], self.speed[1])), duration=self.lifetime, delay=delay, curve=self.speed_curve, auto_play=False, auto_destroy=should_destroy))
        if self.end_size != self.start_size:
            self.anims.append(m.animate_scale(self.end_size, duration=self.lifetime, delay=delay, curve=self.size_curve, auto_play=False, auto_destroy=should_destroy))
    
        if self.end_color != self.start_color:
            self.anims.append(m.animate_color(random.choice(self.end_color), duration=self.lifetime, delay=delay, curve=self.color_curve, auto_play=False, auto_destroy=should_destroy))
    
        if self.spin:
            self.anims.extend(m.animate_rotation(self.spin * self.lifetime, duration=self.lifetime, delay=delay, curve=self.spin_curve, auto_play=False, auto_destroy=should_destroy))

        self.anims.append(m.animate_y(self.bounce, duration=self.lifetime, delay=delay, curve=self.bounce_curve, auto_play=False, auto_destroy=should_destroy))
        # m.animate_y(self.sway, duration=self.lifetime, delay=delay, curve=self.sway_curve)

        self.anims.append(
            Sequence(
                Wait(self.lifetime+delay),
                Func(self.try_disabling, e),
                started=False,
                auto_destroy=should_destroy,
                name='end_sequence',
            )
        )
        if should_destroy:
            self.anims.append(Sequence(Wait(self.lifetime+delay+(self.spawn_interval*self.num_particles)+.1), Func(destroy, e), auto_destroy=True, name='destroy_particle_sequence'))

        # if self.auto_destroy:
        #     self.anims.append(Sequence(Func(destroy, e, delay=self.lifetime+delay+.05)))
        random.seed(None)
        # self.anims.extend(animations)
        # print('-----', delay, '-------', animations)
        # return animations
        # print('num anims:', len(self.anims))

    # def destroy(self):
    #     if self.name and self.seed is not None:
    #         id = f'{self.name}_{self.seed}'
    #         if id in cache:
    #             del cache[id]

    #     destroy(self)

    def try_enabling(self, particle):
        try:
            particle.enabled = True
        except:
            print('can not enable particle because the entity has been destroyed.', self)


    def try_disabling(self, particle):
        try:
            particle.enabled = False
        except:
            print('can not disable particle, already destroyed')

from ursina.prefabs.vec_field import VecField
from ursina.editor.level_editor import ColorField
class ParticleSystemUI(Entity):
    def __init__(self):
        super().__init__()
        self.parent = camera.ui
        self.ui = Entity(parent=self, enabled=1, position=window.top_left+Vec3(.1,-.1,0), scale=.75, model=Circle(radius=.01))
        i = 0
        for key ,value in _ParticleSystem.default_values.items():
            # print(i, key ,value)
            field = None
            if isinstance(value, Vec3):
                field = VecField(value, parent=self.ui)
                
            elif isinstance(value, bool):
                # print('---aaa')
                field = CheckBox(parent=self.ui, x=.025, value=value)
            
            
            elif isinstance(value, int):
                field = VecField(value, parent=self.ui)

            elif isinstance(value, Color):
                field = ColorField(attr_name='color', is_shader_input=False, value=value, parent=self.ui, scale_y=.05)
                
            if field:
                field.y = -i * .05
                Text(text=key, parent=field, y=.5, z=-1, x=.5, world_scale=20)
                i += 1
            else:
                print('no field for:', key, value)
        print('made fields')

    def input(self, key):
        combo = ['control', 'shift' , 'alt', 'p', 'a']
        if key in combo and all([held_keys[e] for e in combo]):
            self.ui.enabled = not self.ui.enabled






if __name__ == '__main__':
    from ursina.ursinamath import rotate_around_point_2d
    app = Ursina()

    player = Entity(model='wireframe_cube', color=color.magenta, origin_y=-.5, alpha=1)
    run_particles = ParticleSystem(
        parent=player,
        scale=1,
        speed=1,
        spawn_interval=.05,
        num_particles=1,
        mesh='icosphere',
        world_space=True,
        end_color = color.red,
        end_size=0,
        direction_randomness=Vec3(360),
        auto_play=True,
        loop_every=.1,
        # name='run particles',
    )
    EditorCamera()
    window.color = color.black

    hit_impact_particles = dict(position=player.position+Vec3.up, scale=.5,
        speed=4,
        lifetime=.15,
        auto_play=False,
        num_particles=5,
        direction_randomness=Vec3(0,0,360),
        move_directions='up',
        billboard=True,
        start_size=Vec3(1,2,1),
        end_size=Vec3(.5,.25,.5),
        name='hit_impact', seed=0,
    )
    burst_particles = dict(position=player.position, scale=.5,
        speed=3,
        lifetime=.125,
        auto_play=False,
        num_particles=6,
        direction_randomness=Vec3(360,360,360),
        move_directions='up',
        mesh=Cone(3, radius=.3),
        start_size=(1,1.5,1),
        end_size=0,
        size_curve = curve.linear,
        start_color = (color.gray, color.light_gray),
        end_color = (color.gray, color.light_gray),
        name='burst', seed=0,
    )
    power_up_particles = dict(position=player.position+Vec3(0,.5,0), scale=(.5,1.5,.5),
        speed=2,
        lifetime=.2,
        auto_play=False,
        # direction_randomness=Vec3(360,360,360),
        move_directions='up',
        mesh='diamond',
        start_size=.5,
        end_size=.5,
        size_curve = curve.linear,
        start_color = (color.gray, color.light_gray),
        end_color = (color.gray, color.light_gray),

        num_particles=0,
        spawn_points = [v.xzy for v in Circle(radius=3).vertices][::-1],
        spawn_type = 'random',
        spawn_interval=.0125,
        # loop=True
        name='power_up_particles', seed=0,
    )
    heal_particles = (
        dict(position=player.position + Vec3(0,.5,0), scale=.5,
            start_size = Vec3(1,4,1)* .5,
            end_size = Vec3(0,5,0) * .5,
            speed=4,
            lifetime=.5,
            auto_play=False,
            direction_randomness=Vec3(0,360,0),
            move_directions='up',
            mesh='diamond',
            size_curve = curve.linear,
            start_color = (color.cyan, hsv(300,.5,1)),
            end_color = (color.lime, color.magenta),
            color_curve=curve.linear,
            num_particles=0,
            spawn_points = [v.xzy for v in Circle(radius=3).vertices][::-1],
            spawn_type = 'random',
            spawn_interval=.0125,
            name='heal', seed=0,
        )
        ,
        dict(position=player.position+Vec3(0,.5,0), scale=(.5,.5,.5),
            speed=1,
            lifetime=.5,
            auto_play=False,
            direction_randomness=Vec3(360,360,360),
            move_directions='up',
            mesh='icosphere',
            start_size=.5,
            end_size=0,
            size_curve = curve.linear,
            start_color = color.cyan,
            end_color = color.blue,
            color_curve=curve.linear,
            num_particles=0,
            spawn_points = [v.xzy for v in Circle(radius=3).vertices][::-1],
            spawn_type = 'random',
            spawn_interval=.0125,
            name='heal_dust', seed=0,
        )
    )

    if not load_model('coin.ursinamesh'):
        coin = Cylinder(direction=(0,0,1), height=.1)
        coin.save('coin.ursinamesh')

    gold_particles = dict(position=player.position+Vec3(0,1,0), scale=.5,
        end_size = Vec3(1),
        speed=5,
        lifetime=1,
        auto_play=False,
        direction_randomness=Vec3(0,360,0),
        spin=Vec3(0,15,0) * 10,
        # spin_curve=curve.linear,
        mesh='coin',
        # shader=matcap_shader,
        # texture='matcap_1',
        start_color = (color.yellow, color.white),
        # end_color = (color.gold, hsv(40,.9,.9)),
        end_color = (color.gold, hsv(40,.9,.9)),
        color_curve=curve.out_expo,
        num_particles=0,
        spawn_points = [v.xzy for v in Circle(radius=3).vertices][::-1],
        move_directions=[v.xzy.normalized() for v in Circle(radius=3).vertices][::-1],
        spawn_type = 'sequential',
        spawn_interval=.01,

        origin_y=-.5,
        bounce=-2,
        name='gold_particles', seed=0
    )

    landing_dust_particles = dict(position=player.position+Vec3(0,.5,0), scale=1,
        end_size = Vec3(0),
        size_curve=curve.linear,
        speed=4,
        speed_curve=curve.out_circ,
        lifetime=.75,
        auto_play=False,
        direction_randomness=Vec3(0,360,0),
        spin=Vec3(0,15,0) * 10,
        # spin_curve=curve.linear,
        mesh='icosphere',
        start_color = (color.white, color.white),
        end_color = (color.light_gray, color.light_gray),
        color_curve=curve.out_expo,
        num_particles=10,
        spawn_type = 'burst',
        name='landing_dust', seed=0,

        shader=matcap_shader,
        texture='matcap_1',
    )


    jump_effects = (
        dict(
            position=player.position+Vec3(0,.25,0), scale=.5,
            start_size = Vec3(.25,2,.25),
            end_size = Vec3(0,8,0),
            speed=8,
            lifetime=.25,
            auto_play=False,
            direction_randomness=Vec3(0,360,0),
            move_directions='up',
            mesh='diamond',
            size_curve = curve.in_expo,
            start_color = (color.smoke, hsv(0,0,.9)),
            end_color = (color.gray, ),
            color_curve=curve.in_expo,
            num_particles=0,
            spawn_points = [v.xzy for v in Circle(radius=3, resolution=6).vertices][::-1],
            spawn_type = 'random',
            spawn_interval=.0125,

            name='jump_lines',
            seed=0,
        )
        ,
        dict(position=player.position + Vec3(0,.5,0), scale=1,
            start_size = Vec3(.25),
            end_size = Vec3(0),
            size_curve=curve.linear,
            speed=(1.5,2.5),
            speed_curve=curve.out_circ,
            lifetime=1,
            direction_randomness=Vec3(0,360,0),
            rotation_randomness=Vec3(360,360,360),
            spin=Vec3(15) * 20,
            mesh='diamond',
            start_color = (color.white, color.white),
            end_color = (color.light_gray, color.light_gray),
            color_curve=curve.out_expo,
            num_particles=10,
            spawn_type = 'burst',
            spawn_interval=.005,
            bounce=-1,
            auto_play=False,

            name='jump_dust',
            seed=0,
        )
    )

    gems = (
        dict(
            position=player.position+Vec3(0,.5,0), scale=.5,
            start_size = Vec3(1,1.5,1) * .5,
            end_size = Vec3(1,1.5,1) * .0,
            speed_curve=curve.combine(curve.zero, curve.out_circ, .2),
            auto_play=False,
            mesh='diamond',
            size_curve = curve.combine(curve.in_back, curve.linear, .3),
            start_color = (color.white),
            spin=Vec3(200,200,200),
            rotation_randomness=Vec3(360),
            num_particles=0,
            spawn_points = [v.xzy for v in Circle(radius=.75, resolution=5).vertices][::-1],
            move_directions='forward',
            spawn_type = 'sequential',
            speed=5,
            lifetime=2,
            delay=.1,
            spawn_interval=.05,
            shader=matcap_shader,
            texture='matcap_dall_e',
            unlit=True,
            bounce=2,
            bounce_curve=curve.combine(curve.out_expo, curve.reverse(curve.linear), .2),
            name='spawn_gems',
            seed=0,
        ),

        dict(
            position=player.position+Vec3(0,.5,0), scale=.5,
            speed=1,
            lifetime=.4,
            auto_play=False,
            num_particles=6,
            direction_randomness=Vec3(360,360,360),
            move_directions='up',
            mesh=Cone(3, radius=.3),
            start_size=(1,1.5,1),
            end_size=0,
            size_curve = curve.linear,
            start_color = (color.white, ),
            end_color = (color.azure, color.cyan),
            color_curve=curve.out_expo,
            name='burst', 
            seed=0,
        )
    )

    
    # buttons = (hit_impact_button, burst_button, power_up_button, heal_button, gold_button, landing_dust_button, jump_effect_button)
    buttons = []
    for particle_system_setting in (hit_impact_particles, burst_particles, power_up_particles, heal_particles, gold_particles, landing_dust_particles, jump_effects, gems):
        if not isinstance(particle_system_setting, (tuple, list)):
            particle_system_setting = (particle_system_setting, )
        name = '/'.join([sub_system.get('name', 'unnamed') for sub_system in particle_system_setting])

        play_uncached_button = Button(scale=.1, text=f'{name}\n(uncached)', text_size=.5, color=color.orange)
        def play_uncached(particle_system_setting=particle_system_setting):
            for e in particle_system_setting:
                e |= {'use_cache':False, 'auto_play':True}
                ParticleSystem(**e)
        play_uncached_button.on_click = play_uncached
        buttons.append(play_uncached_button)

        play_button = Button(scale=.1, text=f'{name}\n', text_size=.5, color=color.azure)
        def play(particle_system_setting=particle_system_setting):
            for e in particle_system_setting:
                e |= {'use_cache':True, 'auto_play':True}
                ParticleSystem(**e)
        play_button.on_click = play
        buttons.append(play_button)

        for fps in (12, 30, 60):
            bake_button = Button(scale=.1, text=f'bake\n{name}\n{fps} fps', text_size=.5)
            def bake(particle_system_setting=particle_system_setting):
                for e in particle_system_setting:
                    e |= {'use_cache':False, 'auto_play':False}
                    instance = ParticleSystem(**e)
                    instance.bake(fps=fps)
            bake_button.on_click = bake
            buttons.append(bake_button)


    grid_layout(buttons, max_x=5, offset=((window.aspect_ratio*-.5)+.25,.4), origin=(-.5,.5), spacing=(.2,.2))

    def update():
        h = max((held_keys['gamepad left stick x'], held_keys['d']-held_keys['a']), key=lambda x: abs(x))
        v = max((held_keys['gamepad left stick y'], held_keys['w']-held_keys['s']), key=lambda x: abs(x))
        move_speed = 5
        input_direction = Vec3(h,0,v).normalized()
        input_strength = min(Vec3(h,0,v).length(), 1)
        player.look_at_xz(player.position + input_direction)
        player.position += player.forward * time.dt * move_speed * input_strength
        run_particles.ignore = input_strength < .01



    # ParticleSystemUI()


    ground = Entity(model='plane', scale=8, texture='grass', texture_scale=Vec2(1), color=color.dark_gray)

    # FrameAnimation3d('test_particles_', fps=30, loop=True, position=(4,1,0), color=color.azure)

    def input(key):
        if key == 'space':
            for e in gems:
                ParticleSystem(**e)

  
    app.run()
