from ursina.editor.level_editor import *
import numpy as np

# Define a fallback cube model with all vertices, triangles, and UVs for 27 slices
fallback_model = Mesh(
    vertices=[
        # Vertices for corners, edges, faces, and center
        (-0.5, -0.5, -0.5), (0.0, -0.5, -0.5), (0.5, -0.5, -0.5),  # Bottom-back
        (-0.5,  0.0, -0.5), (0.0,  0.0, -0.5), (0.5,  0.0, -0.5),  # Middle-back
        (-0.5,  0.5, -0.5), (0.0,  0.5, -0.5), (0.5,  0.5, -0.5),  # Top-back

        (-0.5, -0.5,  0.0), (0.0, -0.5,  0.0), (0.5, -0.5,  0.0),  # Bottom-middle
        (-0.5,  0.0,  0.0), (0.0,  0.0,  0.0), (0.5,  0.0,  0.0),  # Center
        (-0.5,  0.5,  0.0), (0.0,  0.5,  0.0), (0.5,  0.5,  0.0),  # Top-middle

        (-0.5, -0.5,  0.5), (0.0, -0.5,  0.5), (0.5, -0.5,  0.5),  # Bottom-front
        (-0.5,  0.0,  0.5), (0.0,  0.0,  0.5), (0.5,  0.0,  0.5),  # Middle-front
        (-0.5,  0.5,  0.5), (0.0,  0.5,  0.5), (0.5,  0.5,  0.5),  # Top-front
    ],
    triangles=[
        # External faces

        # Front face
        18, 19, 21, 18, 21, 20,
        19, 22, 21, 19, 25, 22,
        21, 22, 23, 21, 23, 20,

        # Back face
        0, 2, 1, 0, 3, 2,
        1, 4, 3, 1, 5, 4,
        3, 4, 6, 3, 6, 2,

        # Top face
        6, 7, 8, 6, 8, 5,
        7, 16, 8, 7, 13, 16,
        8, 16, 17, 8, 17, 5,

        # Bottom face
        0, 9, 10, 0, 10, 1,
        9, 18, 19, 9, 19, 10,
        10, 19, 20, 10, 20, 1,

        # Left face
        0, 9, 3, 9, 12, 3,
        3, 12, 6, 3, 6, 0,
        12, 15, 6, 12, 18, 15,

        # Right face
        2, 11, 5, 11, 14, 5,
        5, 14, 8, 5, 8, 2,
        14, 17, 8, 14, 23, 17,

        # Internal faces (center cube faces)
        13, 14, 16, 14, 17, 16,
        12, 13, 15, 13, 16, 15,
        15, 16, 18, 16, 19, 18,
        14, 19, 17, 14, 20, 19,
    ],
    uvs=[
        # UVs for front face
        (0, 0), (0.5, 0), (1, 0),  # Bottom row
        (0, 0.5), (0.5, 0.5), (1, 0.5),  # Middle row
        (0, 1), (0.5, 1), (1, 1),  # Top row

        # UVs for back face (repeated UVs)
        (0, 0), (0.5, 0), (1, 0),
        (0, 0.5), (0.5, 0.5), (1, 0.5),
        (0, 1), (0.5, 1), (1, 1),

        # UVs for other faces (repeat or scale as necessary)
        (0, 0), (0.33, 0), (0.66, 0),  # Adjust for subdivisions
        (0, 0.33), (0.33, 0.33), (0.66, 0.33),
        (0, 0.66), (0.33, 0.66), (0.66, 0.66),
    ]
)

# --- Utility Functions ---
def calculate_normals(vertices, triangles):
    """Calculate vertex normals for shading."""
    normals = [Vec3(0, 0, 0) for _ in vertices]
    for i in range(0, len(triangles), 3):
        a, b, c = triangles[i:i+3]
        # Compute the cross product using numpy
        v1 = np.array(vertices[b]) - np.array(vertices[a])
        v2 = np.array(vertices[c]) - np.array(vertices[a])
        normal = Vec3(*np.cross(v1, v2)).normalized()
        # Add the face normal to each vertex normal
        for index in (a, b, c):
            normals[index] += normal
    return [n.normalized() for n in normals]

def highlight_region(mesh, region_type, color=(1, 0, 0, 1)):
    """
    Highlight specific regions of the mesh (corner, edge, face, center).
    """
    highlighted_vertices = []
    for i, v in enumerate(mesh.vertices):
        is_corner = all(abs(v[j]) > 0.4 for j in range(3))
        is_edge = sum(abs(v[j]) > 0.4 for j in range(3)) == 2
        is_face = sum(abs(v[j]) > 0.4 for j in range(3)) == 1
        is_center = not is_corner and not is_edge and not is_face

        if (region_type == 'corner' and is_corner or
                region_type == 'edge' and is_edge or
                region_type == 'face' and is_face or
                region_type == 'center' and is_center):
            highlighted_vertices.append(i)
            Entity(model='sphere', position=v, scale=0.05, color=color)

    return highlighted_vertices

def validate_mesh(mesh):
    """
    Validate that all vertices and UVs are correctly mapped.
    """
    assert len(mesh.vertices) > 0, "Error: Mesh has no vertices."
    assert len(mesh.triangles) % 3 == 0, "Error: Triangles must be divisible by 3."
    assert len(mesh.uvs) == len(mesh.vertices), "Error: UV count must match vertex count."

def limit_subdivision(level, max_level=10):
    """
    Limit subdivision levels to avoid performance issues.
    """
    if level > max_level:
        print(f"Subdivision level {level} exceeds max limit {max_level}. Setting to max.")
        return max_level
    return level


# Update UVs dynamically
def update_uvs(mesh, scale, repeat_factor=(1, 1)):
    uvs = []
    for v in mesh.vertices:
        x, y, z = v
        u = x * scale.x * repeat_factor[0]
        v = y * scale.y * repeat_factor[1]
        uvs.append((u, v))
    mesh.uvs = uvs
    mesh.generate()


# Update stretch_model() to support transformations for internal regions
def stretch_model(mesh, scale, limit=0.25, scale_multiplier=1, repeat_factor=(1, 1), regenerate=False):
    verts = [Vec3(*e) for e in mesh.vertices]
    for i, v in enumerate(verts):
        # Identify which region the vertex belongs to
        is_corner = all(abs(v[j]) >= limit for j in range(3))
        is_edge = sum(abs(v[j]) >= limit for j in range(3)) == 2
        is_face = sum(abs(v[j]) >= limit for j in range(3)) == 1
        is_center = not is_corner and not is_edge and not is_face

        # Stretch based on region
        for j in [0, 1, 2]:
            if is_corner:
                continue  # Corners stay fixed
            elif is_edge:
                if abs(v[j]) >= limit:
                    verts[i][j] += scale[j] / 2 - 0.5
            elif is_face:
                if abs(v[j]) >= limit:
                    verts[i][j] += scale[j] / 2 - 0.5
            elif is_center:
                verts[i][j] *= scale[j]

    # Update the mesh vertices
    mesh.vertices = verts

    # Update normals dynamically
    mesh.normals = calculate_normals(mesh.vertices, mesh.triangles)

    # Update the UVs to reflect the new scale and repeat factor
    update_uvs(mesh, scale, repeat_factor)

    if regenerate:
        mesh.generate()

    # Update the mesh vertices
    mesh.vertices = verts

    # Update the UVs to reflect the new scale and repeat factor
    update_uvs(mesh, scale, repeat_factor)

    if regenerate:
        mesh.generate()



print(f"Looking for 'sliceable_cube.ursinamesh' in: {Path(__file__).parent}")
print(f"Looking for 'sliceable_cube.blend' in: {Path(__file__).parent}")

print(f"Looking for models in: {Path(__file__).parent}")
m = load_model('sliceable_cube.ursinamesh', path=Path(__file__).parent)
if not m:
    print("Error: 'sliceable_cube.ursinamesh' not found. Trying to load 'sliceable_cube.blend'.")
    m = load_model('sliceable_cube.blend', path=Path(__file__).parent)
    if not m:
        print("Error: Could not load 'sliceable_cube.blend'. Please ensure the file exists.")
        print("Using fallback model.")
        m = fallback_model


@generate_properties_for_class()
class SlicedCube(Entity):
    default_values = Entity.default_values | dict(model=None, shader='lit_with_shadows_shader', texture='white_cube', collider='box', name='sliced_cube', scale_multiplier=1) # combine dicts
    def __init__(self, repeat_factor=(1, 1), stretchable_mesh='sliceable_cube', **kwargs):
        kwargs = __class__.default_values | kwargs
        self.repeat_factor = repeat_factor  # Initialize repeat_factor early

        if isinstance(stretchable_mesh, str):
            # Entity(model=stretchable_mesh)
            stretchable_mesh = load_model(stretchable_mesh, use_deepcopy=True)
            print('--------------------', 'asdasdølaksdjkljload:', stretchable_mesh)
            if stretchable_mesh is None:
                print(f"Error: Failed to load model '{stretchable_mesh}'. Using default cube model.")
                stretchable_mesh = fallback_model  # Use the fallback model if loading fails
        self.stretchable_mesh = stretchable_mesh
        # self.original_vertices = model.vertices
        super().__init__(**__class__.default_values | kwargs)
        self.model = deepcopy(self.stretchable_mesh)
        # self.model = Mesh(vertices=self.stretchable_mesh.vertices, uvs=self.stretchable_mesh.uvs)
        if self.model:
            self.model.name = 'cube'
        else:
            print("Error: Model is None. Please check the source files.")
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
        update_uvs(self.model, self.world_scale, self.repeat_factor)  # Use self.repeat_factor here
        self.model.generate()

    def highlight(self, region_type):
        if self.highlighted_region:
            destroy(self.highlighted_region)
        self.highlighted_region = highlight_region(self.model, region_type)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if self.model and name in ('scale', 'scale_x', 'scale_y', 'scale_z', 'transform', 'world_transform'):
            self.generate()



if __name__ == '__main__':
    app = Ursina(borderless=False)
    level_editor = LevelEditor()
    level_editor.goto_scene(0,0)

    sliced_cube = SlicedCube(selectable=True, texture='sliceable_cube_template', shader='unlit_shader', scale_multiplier=1.5)
    if sliced_cube.texture is None:
        print("Warning: Texture 'sliceable_cube_template' not found. Consider adding a default texture.")

    def input(key):
        if key == 'h':
            sliced_cube.highlight('corner')  # Highlight corners
        if key == 'space':
            sliced_cube.generate()


    level_editor.add_entity(sliced_cube)
    app.run()
