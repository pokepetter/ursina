import bpy
import os

blend_file_path = bpy.data.filepath
directory = os.path.dirname(blend_file_path)
file_name = os.path.splitext(os.path.basename(blend_file_path))[0]

bpy.ops.export_scene.obj(
    filepath=os.path.join(directory, 'compressed', file_name + '.obj'),
    check_existing=True,
    axis_forward='Z',
    axis_up='Y',
    filter_glob="*.obj;*.mtl",
    use_selection=False,
    use_animation=False,
    use_mesh_modifiers=True,
    use_edges=False,
    use_smooth_groups=False,
    use_smooth_groups_bitflags=False,
    use_normals=True,
    use_uvs=True,
    use_materials=False,
    use_triangles=True,
    use_nurbs=False,
    use_vertex_groups=False,
    use_blen_objects=True,
    group_by_object=False,
    group_by_material=False,
    keep_vertex_order=False,
    global_scale=1,
    path_mode='AUTO'
)
