import bpy
import os
import sys
from pathlib import Path
from math import degrees
import bmesh


# print('starteddddddddddddddddddd')
# for i, arg in enumerate(sys.argv):
#     print('aaaaaaaaaaarg:', arg)

blender_executable, blend_file = sys.argv[:2]
script_file = sys.argv[4]
out_file_path = sys.argv[5]
decimals = int([e for e in sys.argv if e.startswith('--decimals=')][0][len('--decimals='):])
TRIANGULATE = '--triangulate' in sys.argv


print('-----------------------', 'decimals:', decimals, 'triangulate:', TRIANGULATE)

scene_name = Path(bpy.data.filepath).stem
print('file_name:', scene_name)

code = ''

if not '--models_only' in sys.argv:
    code += '''from ursina import *
from time import perf_counter

scene_parent = Entity()

if __name__ == '__main__':
    app = Ursina()

t = perf_counter()
'''
code += '''
# unique meshes
meshes = {
'''

dg = bpy.context.evaluated_depsgraph_get() #getting the dependency graph
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
objects = [ob for ob in bpy.data.objects if ob.type == 'MESH']
unique_objects = {}
# print('meshes:', meshes)
for ob in objects:
    unique_objects[ob.data.name] = ob


for key, ob in unique_objects.items():
    polygons =[]
    verts = []
    normals = []
    vertex_colors = []
    uvs = []
    indices = []

    mesh = ob.evaluated_get(dg).data
    # for poly in mesh.polygons:
    #     print('---------------poly:', [int(e) for e in poly.vertices])
    if TRIANGULATE:
        # triangulate mesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
        bm.normal_update()
        bm.to_mesh(mesh)
        bm.free()
    else:
        for poly in mesh.polygons:
            # print('---------------poly:', [int(e) for e in poly.vertices])
            polygons.append([int(e) for e in poly.vertices])


    for poly in mesh.polygons:
        indices.extend(poly.vertices)

    if TRIANGULATE:
        for idx in indices:
            v = mesh.vertices[idx]
            verts.append((round(v.co[0],decimals),round(v.co[2],decimals),round(v.co[1],decimals)))
    else:
        verts = [(round(v.co[0],decimals),round(v.co[2],decimals),round(v.co[1],decimals)) for v in mesh.vertices]

    if '--vertex_colors' in sys.argv and 'Color' in mesh.attributes:
        color_data = mesh.attributes['Color'].data
        vertex_colors_data = [[round(e,4) for e in (color_data[vertex.index].color_srgb)] for vertex in mesh.vertices]
        vertex_colors = [vertex_colors_data[idx] for idx in indices]

    if '--normals' in sys.argv:
        for idx in indices:
            v = mesh.vertices[idx]
            normals.append((v.normal[0], v.normal[2], v.normal[1]))
    # average the vertex normals to get face normals
        sharp_normals = []
        for i in range(0, len(normals), 3):
            averaged_normal = (
                round(sum((normals[i][0], normals[i+1][0], normals[i+2][0])) / 3, decimals),
                round(sum((normals[i][1], normals[i+1][1], normals[i+2][1])) / 3, decimals),
                round(sum((normals[i][2], normals[i+1][2], normals[i+2][2])) / 3, decimals),
                )
            for j in range(3):
                sharp_normals.append(averaged_normal)

        normals = sharp_normals


    if '--uvs' in sys.argv:
        uv_layer = mesh.uv_layers.active
        if uv_layer and len(uv_layer.data) > 0:
            uvs = [tuple(round(e, decimals) for e in data.uv) for data in uv_layer.data]



    code += f'''
'{mesh.name}' : Mesh(
    vertices={str(verts).replace(' ', '')},
    triangles={polygons},
    normals={str(normals).replace(' ', '')},
    colors={str(vertex_colors).replace(' ', '')},
    uvs={str(uvs).replace(' ', '')},
),
'''

code += '}\n'

if '--models_only' in sys.argv:
    print('sucessfully exported blender models')
    with open(out_file_path, 'w') as f:
        f.write(code)

else:
    # write entities
    code += '''print('loaded models:', perf_counter() - t)\n'''
    code += '''t = perf_counter()\n'''


    for ob in objects:
        if '--skip_hidden' in sys.argv and ob.hide_get() == True:
            continue

        #deselect all but just one object and make it active
        bpy.ops.object.select_all(action='DESELECT')
        rotation = [degrees(e) for e in ob.matrix_world.to_euler()]

        code += f'''
scene_parent.{ob.name.replace('.', '_')} = Entity(
    name=\'{ob.name}\',
    parent=scene_parent,
    position=Vec3({round(ob.location.x,5)}, {round(ob.location.z,5)}, {round(ob.location.y,5)}),
    rotation=({round(-rotation[0],5)}, {round(-rotation[2],5)}, {round(rotation[1],5)}),
    scale=Vec3({round(ob.scale.x,5)}, {round(ob.scale.z,5)}, {round(ob.scale.y,5)}),
    '''

        code += f'''model=copy(meshes['{ob.data.name}']),'''
        # code += f'''model='cube','''

        if ob.active_material:
            color = ob.active_material.diffuse_color
            code += f'''
    color=({round(color[0],5)}, {round(color[1],5)}, {round(color[2],5)}, {round(color[3],5)}),'''

        code += f'''
    ignore=True,
    )'''
    code += '''\n\nscene_parent.meshes = meshes'''
    code += '''\nprint('created entities:', perf_counter() - t)\n'''

    code += '''
if __name__ == '__main__':
    EditorCamera()
    app.run()
'''

    # return code
    print('sucessfully exported blender scene')
    with open(out_file_path, 'w') as f:
        f.write(code)
