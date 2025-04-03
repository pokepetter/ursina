from ursina.editor.level_editor import *
from ursina.shaders import colored_lights_shader

class PokeShape(Entity):
    default_values = Entity.default_values | dict(
        name='poke_shape',
        # make_wall=True,
        wall_height=1.0,
        # wall_thickness=.1,
        subdivisions=0,
        smoothing_distance=.1,
        points=[Vec3(-.5,0,-.5), Vec3(.5,0,-.5), Vec3(.5,0,.5), Vec3(-.5,0,.5)],
        collider_type='None',
        texture='grass',
        texture_scale=Vec2(.125, .125),
        # shader_inputs={'side_texture':Func(load_texture, 'grass'), }

    ) # combine dicts

    gizmo_color = color.violet

    def __init__(self, edit_mode=False, points=None, **kwargs):
        kwargs = __class__.default_values | kwargs
        self.ready = False
        super().__init__(name=kwargs['name'])

        self.original_parent = LEVEL_EDITOR
        self.selectable = True
        self.highlight_color = color.blue
        # self._point_gizmos = LoopingList([Entity(parent=self, original_parent=self, position=e, selectable=False, name='PokeShape_point', is_gizmo=True) for e in kwargs['points']])
        self.model = Mesh()
        self.add_new_point_renderer = Entity(model=Mesh(mode='point', vertices=[], thickness=.075), color=color.white, alpha=.5, texture='circle', unlit=True, is_gizmo=True, selectable=False, enabled=False, always_on_top=True)
        self.add_collider = False
        self._wall_parent = None
        self.wall_height = kwargs['wall_height']
        self.subdivisions =  kwargs['subdivisions']
        self.smoothing_distance = kwargs['smoothing_distance']

        self._point_gizmos = []
        if not points:
            self.points = __class__.default_values['points']
        else:
            self.points = points

        self.texture = kwargs['texture']

        self.position = kwargs['position']
        for key in Entity.default_values.keys():
            if key == 'model':
                continue
            setattr(self, key, kwargs[key])

        # if edit_mode:
        self.edit_mode = edit_mode

        self.generate()
        self.ready = True


    def draw_inspector(self):
        return {'edit_mode': bool, 'wall_height': float, 'subdivisions':int, 'smoothing_distance':float}


    def generate(self):
        # print('--------------', self.texture_scale)
        import tripy
        # if not self.model:
        #     return
        self._point_gizmos = LoopingList([e for e in self._point_gizmos if e])   # ensure deleted points are removed
        polygon = LoopingList(Vec2(*e.get_position(relative_to=self).xz) for e in self._point_gizmos)

        if self.subdivisions:
            for j in range(self.subdivisions):
                smooth_polygon = LoopingList()
                for i, p in enumerate(polygon):
                    smooth_polygon.append(lerp(p, polygon[i-1], self.smoothing_distance))
                    smooth_polygon.append(lerp(p, polygon[i+1], self.smoothing_distance))
                polygon = smooth_polygon

        triangles = tripy.earclip(polygon)
        self.model.vertices = []
        for tri in triangles:
            for v in tri:
                self.model.vertices.append(Vec3(v[0], 0, v[1]))

        self.model.uvs = [Vec2(v[0],v[2])*1 for v in self.model.vertices]
        self.model.normals = [Vec3(0,1,0) for i in range(len(self.model.vertices))]
        self.model.generate()
        # self.texture = 'grass'
        # [destroy(e) for e in self.wall_parent.children]
        # print('-------------', self.make_wall, self.wall_parent)
        if self._wall_parent:
            # print('destroy old wall parent')
            destroy(self._wall_parent)
            self._wall_parent = None

        if self.wall_height:
            if not self._wall_parent:
                # print('make new wall parent')
                self._wall_parent = Entity(parent=self, model=Mesh(), color=color.dark_gray, add_to_scene_entities=False, shader=colored_lights_shader)

            # polygon_3d = [Vec3(e[0], 0, e[1]) for e in polygon]
            # polygon_3d.append(polygon_3d[0])
            # self.wall_parent.model = Pipe(base_shape=Quad(scale=(self.wall_thickness, self.wall_height)), path=polygon_3d)
            # self.wall_parent.model = Pipe(polygon_3d, path=[Vec3(0,0,0), Vec3(0,-10,0)])
            wall_verts = []
            for i, vert in enumerate(polygon):
                vert = Vec3(vert[0], 0, vert[1])
                next_vert = Vec3(polygon[i+1][0], 0, polygon[i+1][1])

                wall_verts.extend((
                    vert,
                    vert + Vec3(0,-self.wall_height,0),
                    next_vert,

                    next_vert,
                    vert + Vec3(0,-self.wall_height,0),
                    next_vert + Vec3(0,-self.wall_height,0),
                ))
            #     # wall = Entity(model='cube', origin_x=-.5, scale=.1, position=vert, scale_x=distance(vert, next_vert), color=color.blue, parent=self._wall_parent, add_to_scene_entities=False)
            #     # wall.look_at(next_vert, 'right')
            #
            self._wall_parent.model.vertices = wall_verts
            self._wall_parent.model.generate_normals(False)
            self._wall_parent.model.generate()


        # if self.add_collider:
        #     self.collider = self.model

        if self.edit_mode:
            self.add_new_point_renderer.model.vertices = []
            for i, e in enumerate(self._point_gizmos):
                self.add_new_point_renderer.model.vertices.append(lerp(self._point_gizmos[i].world_position, self._point_gizmos[i+1].world_position, .5))
                # self.add_new_point_renderer.model.vertices.append(self._point_gizmos[i].world_position)
            self.add_new_point_renderer.model.generate()


    def __deepcopy__(self, memo):
        changes = self.get_changes(__class__)

        _copy = __class__(texture_scale = self.texture_scale, **changes)
        _copy.texture_scale = self.texture_scale
        # print('---------------', _copy.texture_scale)
        return _copy


    @property
    def points(self):
        return [e.position for e in self._point_gizmos]

    @points.setter
    def points(self, value):
        [destroy(e) for e in self._point_gizmos]
        self._point_gizmos = LoopingList([Entity(parent=self, original_parent=self, position=e, selectable=False, name='PokeShape_point', is_gizmo=True, enabled=False) for e in value])
        LEVEL_EDITOR.entities.extend(self._point_gizmos)


    @property
    def edit_mode(self):
        return getattr(self, '_edit_mode', False)

    @edit_mode.setter
    def edit_mode(self, value):
        self._edit_mode = value


        print('set edit mode', value)
        if value:
            [setattr(e, 'selectable', False) for e in LEVEL_EDITOR.entities if not e == self]
            for e in self._point_gizmos:
                if not e in LEVEL_EDITOR.entities:
                    LEVEL_EDITOR.entities.append(e)

            [setattr(e, 'selectable', True) for e in self._point_gizmos]
            LEVEL_EDITOR.gizmo.subgizmos['y'].enabled = False
            LEVEL_EDITOR.gizmo.fake_gizmo.subgizmos['y'].enabled = False
            self.add_new_point_renderer.enabled = True
            self.collider = None
        else:
            [LEVEL_EDITOR.entities.remove(e) for e in self._point_gizmos if e in LEVEL_EDITOR.entities]
            [setattr(e, 'selectable', True) for e in LEVEL_EDITOR.entities]
            if True in [e in LEVEL_EDITOR.selection for e in self._point_gizmos]: # if point is selected when exiting edit mode, select the poke shape
                LEVEL_EDITOR.selection = [self, ]

            LEVEL_EDITOR.gizmo.subgizmos['y'].enabled = True
            LEVEL_EDITOR.gizmo.fake_gizmo.subgizmos['y'].enabled = True
            self.add_new_point_renderer.enabled = False
            self.collider = 'mesh'
        LEVEL_EDITOR.render_selection()

    # @property
    # def wall_height(self):
    #     return self._wall_height
    # @wall_height.setter
    # def wall_height(self, value):
    #     self._wall_height = value
    #     self.generate()

    def update(self):
        if self.edit_mode:
            if mouse.left or held_keys['d']:
                LEVEL_EDITOR.render_selection()
                self.generate()


    def input(self, key):
        combined_key = input_handler.get_combined_key(key)
        if combined_key == 'tab':
            if not LEVEL_EDITOR.selection:
                self.edit_mode = False

            if self in LEVEL_EDITOR.selection or True in [e in LEVEL_EDITOR.selection for e in self._point_gizmos]:
                self.edit_mode = not self.edit_mode

        if self.edit_mode and (key == 'left mouse down' or key == 'd'):
            if LEVEL_EDITOR.selector.get_hovered_entity():
                return
            points_in_range = [(distance_2d(world_position_to_screen_position(v), mouse.position), v) for v in self.add_new_point_renderer.model.vertices]
            points_in_range = [e for e in points_in_range if e[0] < .075/2]
            points_in_range.sort()

            closest_point = None
            if not points_in_range:
                return

            closest_point = points_in_range[0][1]
            i = self.add_new_point_renderer.model.vertices.index(closest_point)

            new_point = Entity(parent=self, original_parent=self, position=lerp(self._point_gizmos[i].position, self._point_gizmos[i+1].position, .5), selectable=True, is_gizmo=True)
            LEVEL_EDITOR.entities.append(new_point)
            self._point_gizmos.insert(i+1, new_point)
            LEVEL_EDITOR.render_selection()
            if key == 'd':
                LEVEL_EDITOR.quick_grabber.input('d')


        elif key == 'space':
            self.generate()

        # elif key == 'double click' and LEVEL_EDITOR.selector.get_hovered_entity() == self:
        #     self.edit_mode = True
        #
        # elif key == 'double click' and not LEVEL_EDITOR.selector.get_hovered_entity():
        #     self.edit_mode = False

        elif self.edit_mode and key.endswith(' up'):
            invoke(self.generate, delay=3/60)

    # def __setattr__(self, name, value):
    #     if name == 'model' and hasattr(self, 'model') and self.model and not isinstance(value, Mesh):
    #         print_info('can\'t set model of PokeShape')
    #         return
    #
    #     super().__setattr__(name, value)


if __name__ == '__main__':
    app = Ursina(borderless=False)

    level_editor = LevelEditor()
    level_editor.goto_scene(0,0)
    # cube = WhiteCube(selectable=True)
    # level_editor.entities.append(PokeShape())
    level_editor.entities.append(PokeShape(points=[Vec3(-6.89023, 0, -5.93539), Vec3(-5.63213, 0, -6.7236), Vec3(-3.06749, 0, -7.45143), Vec3(0.883525, 0, -6.64059), Vec3(6.21342, 0.000496293, -5.19114), Vec3(11.1816, 0.000748294, -1.60608), Vec3(13.0414, 0.000874309, 0.223267), Vec3(12.6511, 0.0010004, 2.84322), Vec3(9.07899, 0.000750429, 5.98706), Vec3(5.59802, 0.000500321, 5.69713), Vec3(3.45835, 0.000375334, 7.03647), Vec3(2.95372, 0.000250343, 9.16615), Vec3(4.31376, 0.00012526, 9.91672), Vec3(5.6031, 0, 12.5358), Vec3(4.99113, 0.00049994, 13.8873), Vec3(3.37031, 0.000749853, 15.6645), Vec3(-0.513243, 0.000874871, 16.5425), Vec3(-2.08884, 0.000999762, 15.3409), Vec3(-3.86994, 0.000500111, 16.2354), Vec3(-5.61374, 0.000375315, 18.7785), Vec3(-5.64462, 0.000250529, 22.5197), Vec3(-18.9718, 0.000125618, 15.9756), Vec3(-14.6812, 0, 10.564), Vec3(-14.2555, 0, 7.90265), Vec3(-13.5866, 0, 4.08694), Vec3(-10.7991, 0, 1.16432), Vec3(-9.05981, 0, 1.75484), Vec3(-7.52061, 0, 0.920164), Vec3(-6.02536, 0, -1.79266), Vec3(-7.2474, 0, -3.23652)]))
    app.run()
