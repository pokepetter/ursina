import bpy
import os
import sys


blend_file_path = bpy.data.filepath
filepath = sys.argv[-1]


bpy.ops.export_scene.obj(
    filepath=filepath,
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
