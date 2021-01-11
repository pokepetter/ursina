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
    mesh = ob.evaluated_get(dg).data

    # triangulate mesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    verts = []
    normals = []
    vertex_colors = []
    uvs = []

    for poly in mesh.polygons:
        face_normal_x, face_normal_y, face_normal_z = 0, 0, 0

        for idx in poly.vertices:
            v = mesh.vertices[idx]
            verts.append((round(v.co[0],4),round(v.co[2],4),round(v.co[1],4)))
            normals.append((v.normal[0], v.normal[2], v.normal[1]))

    # average the vertex normals ot get face normals
    sharp_normals = []
    for i in range(0, len(normals), 3):
        averaged_normal = (
            round(sum((normals[i][0], normals[i+1][0], normals[i+2][0])) / 3, 5),
            round(sum((normals[i][1], normals[i+1][1], normals[i+2][1])) / 3, 5),
            round(sum((normals[i][2], normals[i+1][2], normals[i+2][2])) / 3, 5),
            )
        for j in range(3):
            sharp_normals.append(averaged_normal)

    normals = sharp_normals

    color_layer = mesh.vertex_colors.active
    if color_layer and len(color_layer.data) > 0:
        vertex_colors = [tuple(round(e, 4) for e in data.color) for data in color_layer.data]


    uv_layer = mesh.uv_layers.active
    if uv_layer and len(uv_layer.data) > 0:
        uvs = [tuple(round(e, 4) for e in data.uv) for data in uv_layer.data]



    code += f'''
'{mesh.name.replace('.', '_')}' : Mesh(
    vertices={verts},
    normals={normals},
    colors={vertex_colors},
    uvs={uvs},
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
        if '--skip-hidden' in sys.argv and ob.hide_get() == True:
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

        code += f'''model=deepcopy(meshes['{ob.data.name.replace('.', '_')}']),'''
        # code += f'''model='cube','''

        if ob.active_material:
            color = ob.active_material.diffuse_color
            code += f'''
    color=({round(color[0],5)}, {round(color[1],5)}, {round(color[2],5)}, {round(color[3],5)}),'''

        code += f'''
    ignore=True,
    )'''

    code += '''\nprint('created entities:', perf_counter() - t)'''
    #        if ob.parent:
    #            code += f'''parent=self.{ob.name.replace('.', '_')}'''



        #This has to be done every time the object updates:
        # ob = ob.evaluated_get(dg) #this gives us the evaluated version of the object. Aka with all modifiers and deformations applied.
        # mesh = ob.to_mesh() #turn it into the mesh data block we want.
        # verts = []
        # tris = []
        # uvs = []
        # normals = []
        # vertex_colors = []

        # for poly in mesh.polygons:
        #     tris.append(tuple(e for e in poly.vertices))
        # # for poly in mesh.polygons:
        # #     for idx in poly.vertices:
        # #         verts.append(mesh.vertices[idx])
        # #         normal = mesh.vertices[idx].normal
        # #         n = (normal[0], normal[1], normal[2])
        # #         normals.append(n)
        #
        #
        # color_layer = mesh.vertex_colors.active
        # if color_layer and len(color_layer.data) > 0:
        #     if not vertex_colors:
        #         vertex_colors = [(1,1,1,1) for e in mesh.vertices]
        #
        #     i = 0
        #     for poly in mesh.polygons:
        #         for idx in poly.vertices:
        #             vertex_colors[idx] = tuple(round(e, 4) for e in color_layer.data[i].color)
        #             i += 1
        #
        # uv_layer = mesh.uv_layers.active
        # if uv_layer and len(uv_layer.data) > 0:
        #     if not uvs:
        #         uvs = [(0,0) for e in mesh.vertices]
        #
        #     i = 0
        #     for poly in mesh.polygons:
        #         for idx in poly.vertices:
        #             uvs[idx] = tuple(round(e, 4) for e in uv_layer.data[i].uv)
        #             i += 1


    #     code += f'''
    # model=Mesh('''
    #     # code += f'''
    #     # vertices=[{', '.join([f'Vec3({v.co[0]}, {v.co[2]}, {v.co[1]})' for v in verts])}],'''
    #
    #     code += f'''
    #     vertices=[{', '.join([f'Vec3({round(v.co[0], 4)}, {round(v.co[2], 4)}, {round(v.co[1], 4)})' for v in mesh.vertices])}],
    #     triangles={tris},'''
    #
    #     code += f'''
    #     normals=({' ,'.join([f'Vec3({round(v.normal[0], 4)}, {round(v.normal[2], 4)}, {round(v.normal[1], 4)})' for v in mesh.vertices])}),'''
    #     # code += f'''
    #     # normals=({' ,'.join([f'Vec3({str(n[0])[5:]}, {n[2]}, {n[1]})' for v in normals])}),'''
    #
    #     if uvs:
    #         code += f'''
    #     uvs={uvs},'''
    #
    #     if vertex_colors:
    #         code += f'''
    #     colors={vertex_colors},'''
    #
    #     code += '\n    )'
    #     code += '\n)'



    code += '''
if __name__ == '__main__':
    EditorCamera()
    app.run()
'''

    # return code
    print('sucessfully exported blender scene')
    with open(out_file_path, 'w') as f:
        f.write(code)
