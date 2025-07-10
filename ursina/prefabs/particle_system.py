from ursina import *
from ursina.scripts.property_generator import generate_properties_for_class
from ursina.shaders.unlit_shader import unlit_shader

# _instances = dict() # keeps track of all the instances so we can make a menu that lists all instances, with the option for baking them.

cache = dict()
# If a name and seed is provided, it will replay the instance if it exists.
# This will be faster to play since you only have to instantiate the paritcles and animations once.
# However, this means you can only have one instance playing at the same time.
# If the particle effect has been baked, it will instead load an FrameAnimation3D.



def play_particle_system(name, use_cache=True, auto_play=True, auto_destroy=True, unscaled=False, **kwargs):
    # print('try loading particle system:', name)
    if name in cache:
        animation_texture = cache[name]
    else:
        animation_texture = load_texture(f'{name}_*_baked_fps*_bounds*.png')
        cache[name] = animation_texture

    if animation_texture:   # if the particle system has been baked
        vat_instance = vertex_animation(animation_texture, auto_play=auto_play, unscaled=unscaled)
        if not auto_play:
            vat_instance.enabled = False

        for key, value in kwargs.items():
            setattr(vat_instance, key, value)
        return vat_instance

    whole_file_name = f'{name}.ursinaparticles'
    particle_files = tuple(application.asset_folder.glob(f'**/{whole_file_name}'))
    if not particle_files:
        print_warning('missing particle system:', whole_file_name)
        return

    with particle_files[0].open('r') as f:
        text = f.read()

    relevant_part = 'ParticleSystemContainer(' + text.split('ParticleSystemContainer(',1)[1].split("if __name__ == ")[0]
    particle_container = eval(relevant_part)
    for key, value in kwargs.items():
        setattr(particle_container, key, value)

    for subsystem in particle_container.subsystems:
        for seq in subsystem.anims:
            seq.unscaled = unscaled

    if auto_play:
        particle_container.play()
    if auto_destroy:
        destroy(particle_container, delay=particle_container.total_duration, unscaled=unscaled)

    return particle_container


class ParticleSystemContainer(Entity):
    instances = []

    def __init__(self, subsystems:list, **kwargs):
        super().__init__(**kwargs)
        self.subsystems = subsystems
        for e in self.subsystems:
            e.parent = self
        self.total_duration = max([c.delay + c.total_duration for c in self.subsystems])


    def play(self):
        for e in self.subsystems:
            e.play()


    def bake_to_vertex_animation_texture(entity, name, seed, fps=30):   # bakes all children and animations to a texture
        animations = []
        for c in entity.get_decendants():
            animations.extend(c.anims)

        frames = []
        bake_parent = Entity()
        original_parent = entity.parent
        entity.parent = bake_parent

        duration_per_frame = 1 / fps
        total_duration = max(seq.func_call_time[-1] for seq in entity.animations)
        num_frames = int(total_duration / duration_per_frame)
        if num_frames <= 0:
            raise Exception('can\'t bake particle system with 0 frames')
        print('num_frames:', num_frames)


        for i in range(num_frames):
            bake_parent.model = None
            if not bake_parent.children:
                raise Exception('no particles to bake')

            bake_parent.combine(auto_destroy=False)

            for seq in animations:
                seq.t += duration_per_frame
                seq.started = True
                seq.update()
                seq.started = False

            frames.append(deepcopy(bake_parent.model))
            Entity(model=Mesh(vertices=bake_parent.model.vertices), wireframe=True, color=color.green) # debug render

        entity.parent = original_parent



    def bake(self, name, seed, fps=30):     # bake to vertex animation texture
        from PIL import Image

        animations = []
        for c in self.subsystems:
            animations.extend(c.anims)
            # print('------------',c.total_duration)

        duration_per_frame = 1 / fps
        num_frames = int(self.total_duration / duration_per_frame)
        if num_frames <= 0:
            raise Exception('can\'t bake particle system with 0 frames')

        print('num_frames:', num_frames)

        folder = application.asset_folder / 'particle_system_baked'
        folder.mkdir(parents=True, exist_ok=True)
        frames = []
        bake_parent = Entity()
        original_parent = self.parent
        self.parent = bake_parent

        for i in range(num_frames):
            bake_parent.model = None
            if not self.children:
                raise Exception('no particles to bake')

            bake_parent.combine(auto_destroy=False)

            for seq in animations:
                seq.t += duration_per_frame
                seq.started = True
                seq.update()
                seq.started = False

            frames.append(deepcopy(bake_parent.model))
            # print(bake_parent.model.vertices)
            Entity(model=Mesh(vertices=bake_parent.model.vertices), wireframe=True, color=color.green) # debug render

        self.parent = original_parent

        if not frames:
            raise Exception('Particle system has 0 frames')

        # num_vertices = max(len(e.vertices) for e in frames)
        num_vertices = len(frames[0].vertices)
        if num_vertices <= 0:
            raise Exception('can\'t bake particle system with 0 vertices.')

        min_x, max_x, min_y, max_y, min_z, max_z = 0, 0, 0, 0, 0, 0
        for frame in frames:
            min_x = min(min_x, floor(min(v.x for v in frame.vertices)))
            min_y = min(min_y, floor(min(v.y for v in frame.vertices)))
            min_z = min(min_z, floor(min(v.z for v in frame.vertices)))
            max_x = max(max_x, ceil(max(v.x for v in frame.vertices)))
            max_y = max(max_y, ceil(max(v.y for v in frame.vertices)))
            max_z = max(max_z, ceil(max(v.z for v in frame.vertices)))

        # print('verts:', num_vertices)
        texture_width = num_vertices * 2    # one pixel per vertex. one color per vertex.
        texture_height = len(frames)

        if texture_width > 4096 or texture_height > 4096:
            raise Exception(f'Particle system animation won\'t fit in a 4096x4096 texture: num_frames:{len(frames.vertices)}, vertices:{num_vertices}')

        print(texture_width, texture_height)
        texture = Texture(Image.new(mode="RGB", size=(texture_width, texture_height)))

        for y, frame in enumerate(frames):
            for x, v in enumerate(frame.vertices):
                # v = v - frames[0][x] # get offset from first frame
                texture.set_pixel(x, y, color.rgb(
                    inverselerp(min_x, max_x, v.x),
                    inverselerp(min_y, max_y, v.y),
                    inverselerp(min_z, max_z, v.z))
                )
            for x, c in enumerate(frame.colors):
                texture.set_pixel(x+num_vertices, y, c)

        # Mesh(vertices=frames[0]).save(f'{self.name}_{self.seed}_baked_{min_x}_{max_x}_{min_y}_{max_y}_{min_z}_{max_z}.ursinamesh', folder)
        destroy(bake_parent)

        texture.save(folder / f'{name}_seed{seed}_baked_fps{fps}_bounds{min_x}_{max_x}_{min_y}_{max_y}_{min_z}_{max_z}.png')


def vertex_animation(animation_texture, auto_play=True, unscaled=False):
    from ursina.shaders.vertex_animation_shader import vertex_animation_shader
    instance = Entity(model=Mesh(vertices=[Vec3.zero for i in range(animation_texture.width)]), shader=vertex_animation_shader)

    fps = float(animation_texture.path.stem.split('_fps')[1].split('_')[0])
    min_x, max_x, min_y, max_y, min_z, max_z = [int(e) for e in animation_texture.path.stem.split('_bounds')[1].split('_')]
    animation_texture.filtering = 'bilinear'
    animation_texture.repeat = False

    instance.set_shader_input('pos_min', Vec3(min_x, min_y, min_z))
    instance.set_shader_input('pos_max', Vec3(max_x, max_y, max_z))
    instance.set_shader_input('num_verts', animation_texture.width)
    instance.set_shader_input('frame_texture', animation_texture)
    instance.set_shader_input('total_frames', animation_texture.size[1])
    animation_duration = 1/fps * animation_texture.size[1]
    loop = False

    if auto_play:
        instance.animate_shader_input('frame_index', animation_texture.size[1]-1, duration=animation_duration, loop=loop, curve=curve.linear, resolution=120, unscaled=unscaled)

    if not loop:
        destroy(instance, delay=animation_duration, unscaled=unscaled)
    return instance

def _sample_random(seq, i):
    return random.choice(seq)

def _sample_sequential(seq, i):
    if i >= len(seq):
        raise IndexError(f'{i} out of range. Make sure start_color and end_color lists are the same length as spawn_points when using color_sample_function=\'sequential\'')
    return seq[i]

color_sample_functions = {
    'random' : _sample_random,
    'sequential' : _sample_sequential,
}


@generate_properties_for_class()
class ParticleSystem(Entity):
    default_values = dict(
        start_size=1,
        end_size=0,
        size_curve=curve.in_expo,
        color_curve=curve.in_expo,

        start_color=color.white,
        end_color=color.white,
        color_sample_function='random',    #  'random' / 'sequential'

        start_direction=Vec3(0,0,0),
        direction_randomness=Vec3(0,0,0),
        start_rotation=Vec3(0,0,0),
        rotation_randomness=Vec3(0,0,0),    # rotates the model only, not the direction it moves in
        spin=Vec3(0,0,0),
        spin_curve = curve.linear,

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
        auto_play=False,
        # auto_destroy=True,
        name='',
        seed=None,  # set which random seed to use. int / int tuple/list
    )

    def __init__(self, **kwargs):
        self.original_settings = kwargs

        # invalid_keys = set(kwargs) - set(Entity.default_values | __class__.default_values)
        # if invalid_keys:
        #     raise ValueError(f"Invalid keyword arguments: {', '.join(invalid_keys)}")

        super().__init__(**(__class__.default_values | kwargs))

        if self.num_particles == 0:
            self.num_particles = len(self.spawn_points)

        if not isinstance(self.move_directions, tuple | list):
            self.move_directions = [self.move_directions for i in range(self.num_particles)]
        if not isinstance(self.start_direction, tuple | list):
            self.start_direction = [self.start_direction for i in range(self.num_particles)]

        if not isinstance(self.start_color, tuple | list):
            self.start_color = (self.start_color, )
        if not isinstance(self.end_color, tuple | list):
            self.end_color = (self.end_color, )

        if not isinstance(self.speed, tuple | list):
            self.speed = (self.speed, self.speed)

        self.spawn_points = LoopingList(self.spawn_points)
        self.particles = []
        self.t = 0
        self.total_duration = self.lifetime + (self.num_particles * self.spawn_interval)
        self.is_playing = False

        self.generate()
        if self.auto_play:
            self.play()


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
            [self.generate_particle_animations(
                position=Vec3.zero,
                start_direction=self.start_direction[i],
                move_direction=self.move_directions[i],
                delay=self.delay+(i*self.spawn_interval), i=i)
                for i in range(self.num_particles)]

        elif self.spawn_type == 'random':
            [self.generate_particle_animations(
                position=random.choice(self.spawn_points),
                start_direction=self.start_direction[i],
                move_direction=self.move_directions[i],
                delay=self.delay+(i*self.spawn_interval), i=i)
                for i in range(self.num_particles)]

        elif self.spawn_type == 'sequential':
            [self.generate_particle_animations(
                position=self.spawn_points[i],
                start_direction=self.start_direction[i],
                move_direction=self.move_directions[i],
                delay=self.delay+(i*self.spawn_interval), i=i)
                for i in range(self.num_particles)]


    def play(self):
        self.t = 0
        for e in self.anims:
            e.start()
        self.is_playing = True


    def generate_particle_animations(self, position, start_direction, move_direction, delay=0, i=0):
        if self.seed is None:
            random.seed(None)
        else:
            random.seed(self.seed+i)    # use seed + particle index so the particle system will be somewhat random, but prevent each particle from facing the same direction.

        if len(self.particles) >= self.max_particles:
            return

        model = self.mesh
        if not isinstance(model, str):
            model = deepcopy(model)

        e = Entity(parent=self, scale=self.start_size, position=position, enabled=False)
        # e.rotation = start_direction + Vec3(*[random.uniform(-e/2, e/2) for e in self.direction_randomness])
        e.look_in_direction(start_direction)
        e.rotation += Vec3(*[random.uniform(-e/2, e/2) for e in self.direction_randomness])

        if isinstance(move_direction, str):
            move_direction = getattr(e, move_direction).normalized()
            # e.look_at(e.position + direction)
        graphics = Entity(parent=e, model=model, origin=self.origin, double_sided=self.double_sided, shader=self.shader, texture=self.texture, always_on_top=self.always_on_top, unlit=self.unlit)
        e.graphics = graphics
        graphics.rotation = self.start_rotation + Vec3(*[random.uniform(-e/2, e/2) for e in self.rotation_randomness])

        if self.world_space:
            e.world_parent = scene

        # if self.color_randomness ==
        graphics.color = color_sample_functions[self.color_sample_function](self.start_color, i)
        should_destroy_particles = self.loop_every > 0

        self.anims.append(Sequence(
            Func(self.try_disabling, e),
            Wait(delay),
            Func(self.try_enabling, e),
            Func(setattr, e, 'position', e.position),
            Func(setattr, e, 'rotation', e.rotation),
            Func(setattr, e, 'scale', e.scale),
            Func(setattr, graphics, 'color', graphics.color),
            Func(setattr, graphics, 'rotation', graphics.rotation),
            # Func(setattr, graphics, 'scale', 1),
            Func(setattr, graphics, 'y', graphics.y),
            started=False, auto_destroy=should_destroy_particles, name='start_sequence'))

        RESOLUTION = int(self.lifetime * 60)
        self.anims.extend(e.animate_position(e.position + (move_direction * random.uniform(self.speed[0], self.speed[1])), duration=self.lifetime, delay=delay, curve=self.speed_curve, resolution=RESOLUTION, auto_play=False, auto_destroy=should_destroy_particles))
        if self.end_size != self.start_size:
            self.anims.append(e.animate_scale(self.end_size, duration=self.lifetime, delay=delay, curve=self.size_curve, resolution=RESOLUTION, auto_play=False, auto_destroy=should_destroy_particles))

        if self.end_color != self.start_color:
            self.anims.append(graphics.animate_color(color_sample_functions[self.color_sample_function](self.end_color,i), duration=self.lifetime, delay=delay, curve=self.color_curve, resolution=RESOLUTION, auto_play=False, auto_destroy=should_destroy_particles))

        if self.spin:
            self.anims.extend(graphics.animate_rotation(self.spin * self.lifetime, duration=self.lifetime, delay=delay, curve=self.spin_curve, resolution=RESOLUTION, auto_play=False, auto_destroy=should_destroy_particles))

        self.anims.append(graphics.animate_y(self.bounce, duration=self.lifetime, delay=delay, curve=self.bounce_curve, resolution=RESOLUTION, auto_play=False, auto_destroy=should_destroy_particles))
        # graphics.animate_y(self.sway, duration=self.lifetime, delay=delay, curve=self.sway_curve)

        self.anims.append(
            Sequence(
                Wait(self.lifetime+delay),
                Func(self.try_disabling, e),
                started=False,
                auto_destroy=should_destroy_particles,
                name='end_sequence',
            )
        )
        if self.loop_every > 0:
            self.anims.append(Sequence(
                Wait(delay + self.total_duration + .1),
                Func(destroy, e),
                auto_destroy=True, name='destroy_particle_sequence')
                )

        # if self.loop_every > 0:
        #     destroy(self, delay=delay + self.total_duration + .1)
            # del cache[self.name]
        #     self.anims.append(Sequence(Func(destroy, self, delay=self.lifetime+delay+.05)))
        # if not self.loop_every and not cached:
        # random.seed(None)
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
            particle.model_parent.scale = 1
        except:
            pass
            # print('can not enable particle because the entity has been destroyed.', self)


    def try_disabling(self, particle):
        try:
            # particle.enabled = False
            particle.model_parent.world_scale = Vec3(.001)  # keep enabled and scale to 0 to keep vertices after combine() and make baking easier.
        except:
            pass
            # print('can not disable particle, already destroyed')

# from ursina.prefabs.vec_field import VecField
# from ursina.editor.level_editor import ColorField
# class ParticleSystemUI(Entity):
#     def __init__(self):
#         super().__init__()
#         self.parent = camera.ui
#         self.ui = Entity(parent=self, enabled=1, position=window.top_left+Vec3(.1,-.1,0), scale=.75, model=Circle(radius=.01))
#         i = 0
#         for key ,value in _ParticleSystem.default_values.items():
#             # print(i, key ,value)
#             field = None
#             if isinstance(value, Vec3):
#                 field = VecField(value, parent=self.ui)

#             elif isinstance(value, bool):
#                 # print('---aaa')
#                 field = Checkbox(parent=self.ui, x=.025, value=value)


#             elif isinstance(value, int):
#                 field = VecField(value, parent=self.ui)

#             elif isinstance(value, Color):
#                 field = ColorField(attr_name='color', is_shader_input=False, value=value, parent=self.ui, scale_y=.05)

#             if field:
#                 field.y = -i * .05
#                 Text(text=key, parent=field, y=.5, z=-1, x=.5, world_scale=20)
#                 i += 1
#             else:
#                 print('no field for:', key, value)
#         print('made fields')

#     def input(self, key):
#         combo = ['control', 'shift' , 'alt', 'p', 'a']
#         if key in combo and all([held_keys[e] for e in combo]):
#             self.ui.enabled = not self.ui.enabled


class ParticleSystemUI(Entity):
    def __init__(self, asset_file, particle_system_container):
        super().__init__(parent=camera.ui)
        from ursina import Text
        from ursina.prefabs.window_panel import WindowPanel

        self.asset_file = asset_file
        self.particle_system_container = particle_system_container
        self.seed_slider = Slider(min=0, max=16, step=1, x=-.5-.1, y=-.4, text='seed')
        def preview_particle_system():
            particle_system_container.seed = self.seed_slider.value
            for c in self.particle_system_container.subsystems:
                c.seed = self.seed_slider.value
                c.generate()
            self.particle_system_container.play()

        self.seed_slider.on_value_changed = preview_particle_system

        self.play_button = Button(text='Play', scale=[.1,.05], y=-.4, on_click=preview_particle_system)
        self.ground = Entity(model='wireframe_quad', scale=8, rotation_x=90, alpha=.2)

        self.overwrite_label = Text('Overwrite\nFILE?', scale=.75)
        self.overwrite_button = Button(text='Yes', color=color.azure)
        self.cancel_button = Button(text='Cancel', color=color.black)

        self.overwrite_dialog = WindowPanel(
            title='Overwrite?',
            content=[self.overwrite_label, self.overwrite_button, self.cancel_button],
            parent=self, z=-10, popup=True, enabled=False)

        self.cancel_button.on_click = self.overwrite_dialog.disable
        self.play_baked_buttons = []
        self.bake_buttons = []
        self.render_particle_system_list()

    def input(self, key):
        if key == 'tab':
            self.render_particle_system_list()


    def on_enable(self):
        self.render_particle_system_list()


    def render_particle_system_list(self):
        [destroy(e) for e in self.play_baked_buttons]
        [destroy(e) for e in self.bake_buttons]
        self.play_baked_buttons = []
        self.bake_buttons = []

        vertex_animation_paths = tuple(application.asset_folder.glob(f'**/{self.asset_file.stem}_seed*_baked_fps*_bounds*.png'))

        for vat_path in vertex_animation_paths:
            fps = vat_path.name.split('_fps')[1].split('_',1)[0]
            play_baked_button = Button(parent=self, scale=(.2,.05), text=f'{vat_path.stem}\n(VAT) {fps}FPS', text_size=.5, color=color.green.tint(-.5))
            def play_baked(vat_path=vat_path):
                vertex_animation(Texture(vat_path))
            play_baked_button.on_click = play_baked
            self.play_baked_buttons.append(play_baked_button)

        for target_fps in (12,30,60):
            def _try_bake(target_fps=target_fps):
                animation_texture = load_texture(f'{self.asset_file.stem}_seed*_baked_fps*_bounds*.png')
                if not animation_texture:
                    self.particle_system_container.bake(self.asset_file.stem, self.seed_slider.value, target_fps)
                    return
                if animation_texture.path.exists():
                    print('replace?', animation_texture.path)
                    if fps != target_fps:
                        print(f'{fps} -> {target_fps}', '----------', animation_texture.path.name)
                        base_name = animation_texture.path.stem.split('_seed')[0]
                        seed = animation_texture.path.stem.split('_seed')[1].split('_',1)[0]
                        self.overwrite_dialog.enabled = True
                        self.overwrite_label.text = f'Overwrite\n{animation_texture.path.name}?'
                        self.overwrite_button.on_click = Sequence(
                            animation_texture.path.unlink,
                            Func(self.particle_system_container.bake, base_name, seed, target_fps),
                            self.overwrite_dialog.disable
                            )
                    return

            bake_button = Button(parent=self, scale=(.1,.05), text=f'Bake to VAT\n({target_fps}FPS)', text_size=.5, color=color.orange.tint(-.2))
            bake_button.on_click = _try_bake
            self.bake_buttons.append(bake_button)

        if self.play_baked_buttons:
            grid_layout(self.play_baked_buttons, max_x=2, offset=((window.aspect_ratio*-.5)+.25,.4), origin=(-.5,.5), spacing=(.01,.01))
        if self.bake_buttons:
            grid_layout(self.bake_buttons, max_x=3, offset=((window.aspect_ratio*-.5)+.25+.42,.4), origin=(-.5,.5), spacing=(.01,.01))




if __name__ == '__main__':
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
        loop_every=.1,
        auto_play=True
        # name='run particles',
    )
    EditorCamera()
    window.color = color.black

    # burst_particles = dict(position=player.position, scale=.5,
    #     speed=3,
    #     lifetime=.125,
    #     num_particles=6,
    #     direction_randomness=Vec3(360,360,360),
    #     move_directions='up',
    #     mesh=Cone(3, radius=.3),
    #     start_size=(1,1.5,1),
    #     end_size=0,
    #     size_curve = curve.linear,
    #     start_color = (color.gray, color.light_gray),
    #     end_color = (color.gray, color.light_gray),
    #     name='burst', seed=0,
    # )
    # power_up_particles = dict(position=player.position+Vec3(0,.5,0), scale=(.5,1.5,.5),
    #     speed=2,
    #     lifetime=.2,
    #     # direction_randomness=Vec3(360,360,360),
    #     move_directions='up',
    #     mesh='diamond',
    #     start_size=.5,
    #     end_size=.5,
    #     size_curve = curve.linear,
    #     start_color = (color.gray, color.light_gray),
    #     end_color = (color.gray, color.light_gray),

    #     num_particles=0,
    #     spawn_points = [v.xzy for v in Circle(radius=3).vertices][::-1],
    #     spawn_type = 'random',
    #     spawn_interval=.0125,
    #     # loop=True
    #     name='power_up_particles', seed=0,
    # )





    # landing_dust_particles = dict(position=player.position+Vec3(0,.5,0), scale=1,
    #     end_size = Vec3(0),
    #     size_curve=curve.linear,
    #     speed=4,
    #     speed_curve=curve.out_circ,
    #     lifetime=.75,
    #     direction_randomness=Vec3(0,360,0),
    #     spin=Vec3(0,15,0) * 10,
    #     # spin_curve=curve.linear,
    #     mesh='icosphere',
    #     start_color = (color.white, color.white),
    #     end_color = (color.light_gray, color.light_gray),
    #     color_curve=curve.out_expo,
    #     num_particles=10,
    #     spawn_type = 'burst',
    #     name='landing_dust', seed=0,

    #     shader=matcap_shader,
    #     texture='matcap_1',
    # )


    S = 5
    spawn_points = [Vec3(*[random.uniform(-S,S) for _ in range(3)]) for i in range(1)]
    print(spawn_points)
    particle_system_container = ParticleSystemContainer((
        ParticleSystem(
            # scale=.75 * .5,
            start_size=.5,
            end_size = Vec3(0),
            size_curve=curve.linear,
            speed=1,
            # speed_curve=curve.out_circ,
            lifetime=6,
            direction_randomness=Vec3(0,360,0),
            # spin=Vec3(0,15,0) * 10,
            # spin_curve=curve.linear,
            mesh='icosphere',
            start_color = (color.white, color.white),
            # end_color = (color.light_gray, color.light_gray),
            # color_curve=curve.out_expo,
            num_particles=10,
            spawn_type = 'random',
            name='snow',
            spawn_interval=.2,
            # seed=0,
            loop_every=1,
            spawn_points=spawn_points,
        ),
    ))




    # CAN_RETURN_BAKED = False
    # for particle_system_settings in (hit_impact_particles, burst_particles, power_up_particles, gold_particles, landing_dust_particles, jump_effects):
    #     if not isinstance(particle_system_settings, (tuple, list)):
    #         particle_system_settings = (particle_system_settings, )
    #     if any([e.get('loop_every', False) for e in particle_system_settings]):
    #         # skip looping particle system
    #         continue
    #     for e in particle_system_settings:
    #         e |= {'auto_play':False, }
    #         ParticleSystem(**e)

    particle_system_ui = ParticleSystemUI(Path(__file__), ParticleSystemContainer((run_particles, ), parent=player))
    # particle_system_ui.render_particle_system_list()


    # buttons = (hit_impact_button, burst_button, power_up_button, heal_button, gold_button, landing_dust_button, jump_effect_button)
    # buttons = []
    # for particle_system_setting in (hit_impact_particles, burst_particles, power_up_particles, heal_particles, gold_particles, landing_dust_particles, jump_effects, gems):
    #     if not isinstance(particle_system_setting, (tuple, list)):
    #         particle_system_setting = (particle_system_setting, )
    #     name = '/'.join([sub_system.get('name', 'unnamed') for sub_system in particle_system_setting])

    #     play_uncached_button = Button(scale=.1, text=f'{name}\n(uncached)', text_size=.5, color=color.orange)
    #     def play_uncached(particle_system_setting=particle_system_setting):
    #         for e in particle_system_setting:
    #             ParticleSystem(**e)




    #     if not isinstance(particle_system_setting, (tuple, list)):
    #         particle_system_setting = (particle_system_setting, )
    #     name = '/'.join([sub_system.get('name', 'unnamed') for sub_system in particle_system_setting])

    #     play_uncached_button = Button(scale=.1, text=f'{name}\n(uncached)', text_size=.5, color=color.orange)
    #     def play_uncached(particle_system_setting=particle_system_setting):
    #         for e in particle_system_setting:
    #             e |= {'use_cache':False, 'auto_play':True}
    #             ParticleSystem(**e)
    #     play_uncached_button.on_click = play_uncached
    #     buttons.append(play_uncached_button)

    #     play_button = Button(scale=.1, text=f'{name}\n', text_size=.5, color=color.azure)
    #     def play(particle_system_setting=particle_system_setting):
    #         for e in particle_system_setting:
    #             e |= {'use_cache':True, 'auto_play':True}
    #             ParticleSystem(**e)
    #     play_button.on_click = play
    #     buttons.append(play_button)

    #     for fps in (12, 30, 60):
    #         bake_button = Button(scale=.1, text=f'bake\n{name}\n{fps} fps', text_size=.5)
    #         def _bake(particle_system_setting=particle_system_setting, fps=fps):
    #             for e in particle_system_setting:
    #                 e |= {'use_cache':False, 'auto_play':False}
    #                 instance = ParticleSystem(**e)
    #                 instance.bake(fps=fps)
    #         bake_button.on_click = _bake
    #         buttons.append(bake_button)


    # grid_layout(buttons, max_x=5, offset=((window.aspect_ratio*-.5)+.25,.4), origin=(-.5,.5), spacing=(.01,.01))


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

    app.run()
