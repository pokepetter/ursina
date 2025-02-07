import bpy
import os
import sys


blend_file_path = bpy.data.filepath
filepath = sys.argv[-1]

bpy.ops.wm.obj_export(
    filepath=filepath,
    check_existing=True,
    forward_axis='Z',
    up_axis='Y',
    filter_glob="*.obj;*.mtl",
    export_selected_objects=False,
    export_smooth_groups=False,
    export_normals=True,
    export_uv=True,
    export_materials=True,
    export_colors=True,
    export_triangulated_mesh=True,
    export_curves_as_nurbs=False,
    export_vertex_groups=False,
    global_scale=1,
    path_mode='AUTO'
)
