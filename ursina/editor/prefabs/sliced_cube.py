from ursina.editor.level_editor import *


def stretch_model(mesh, scale, limit=.25, scale_multiplier=1, regenerate=False):
    verts = [Vec3(*e) for e in mesh.vertices]
    mesh.uvs = [Vec2(*e) for e in mesh.uvs]

    for i, v in enumerate(verts):
        for j in [0,1,2]:
            if v[j] <= -limit:
                verts[i][j] += .5 + (scale_multiplier/2)
                verts[i][j] -= scale[j] / 2
                if mesh.uvs:
                    mesh.uvs[i][0] += .5 + (scale_multiplier/2)

            elif v[j] >= limit:
                verts[i][j] -= .5
                verts[i][j] += scale[j] / 2

        verts[i] /= scale

    mesh.vertices = verts
    print('----', mesh.vertices)

    # if mesh.uvs:


    if regenerate:
        mesh.generate()




if not load_model('sliceable_cube.ursinamesh', path=Path(__file__).parent):
    m = load_model('sliceable_cube.blend', path=Path(__file__).parent)
    m.save('sliceable_cube.ursinamesh')



@generate_properties_for_class()
class SlicedCube(Entity):
    default_values = Entity.default_values | dict(model=None, shader='lit_with_shadows_shader', texture='white_cube', collider='box', name='sliced_cube', scale_multiplier=1) # combine dicts
    def __init__(self, stretchable_mesh='sliceable_cube', **kwargs):
        kwargs = __class__.default_values | kwargs

        if isinstance(stretchable_mesh, str):
            # Entity(model=stretchable_mesh)
            stretchable_mesh = load_model(stretchable_mesh, use_deepcopy=True)
            print('--------------------', 'asdasdølaksdjkljload:', stretchable_mesh)
        self.stretchable_mesh = stretchable_mesh
        # self.original_vertices = model.vertices
        super().__init__(**__class__.default_values | kwargs)
        self.model = deepcopy(self.stretchable_mesh)
        # self.model = Mesh(vertices=self.stretchable_mesh.vertices, uvs=self.stretchable_mesh.uvs)
        self.model.name = 'cube'
        self.scale_multiplier = kwargs['scale_multiplier']
        self.scale = kwargs['scale']
        self.texture = kwargs['texture']


    def __deepcopy__(self, memo):
        return eval(repr(self))

    # def scale_getter(self):
    #     return super().scale_getter()

    # def scale_setter(self, value):
    #     super().scale_setter(value)
    #     print('------------uuuuuuuuuu')
    #     if self.model:  # ensure init is done and that there's a Mesh as model
    #         self.generate()

    def generate(self):
        print('update model',self.scale)

        self.model.vertices = self.stretchable_mesh.vertices
        self.model.uvs = self.stretchable_mesh.uvs
        stretch_model(self.model, self.world_scale)
        self.model.generate()

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if self.model and name in ('scale', 'scale_x', 'scale_y', 'scale_z', 'transform', 'world_transform'):
            self.generate()



if __name__ == '__main__':
    app = Ursina(borderless=False)
    level_editor = LevelEditor()
    level_editor.goto_scene(0,0)

    sliced_cube = SlicedCube(selectable=True, texture='sliceable_cube_template', shader='unlit_shader', scale_multiplier=1.5)
    def input(key):
        if key == 'space':
            sliced_cube.generate()


    level_editor.add_entity(sliced_cube)
    app.run()
