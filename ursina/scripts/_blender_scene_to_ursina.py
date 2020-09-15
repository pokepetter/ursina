import bpy
import os
import sys
from pathlib import Path

print(sys.argv)
filepath = sys.argv[-1]
scene_name = Path(bpy.data.filepath).stem
print('file_name:', scene_name)
code = f'''from ursina import *

scene_parent = Entity()\n
'''
dg = bpy.context.evaluated_depsgraph_get() #getting the dependency graph


for collection in bpy.data.collections:
    print(collection.name)
    for ob in collection.all_objects:
        if not ob.type == 'MESH':
            continue

        #deselect all but just one object and make it active
        bpy.ops.object.select_all(action='DESELECT')


        code += f'''
scene_parent.{ob.name.replace('.', '_')} = Entity(
    name=\'{ob.name}\',
    position=Vec3({ob.location.x}, {ob.location.z}, {ob.location.y}),
    rotation=({ob.rotation_euler.x}, {ob.rotation_euler.y}, {ob.rotation_euler.z}),
    scale=Vec3({ob.scale.x}, {ob.scale.z}, {ob.scale.y}),
    ignore=True,
    '''

        if ob.active_material:
            color = ob.active_material.diffuse_color
            code += f'color=color.Color({color[0]}, {color[1]}, {color[2]}, 1),'

#        if ob.parent:
#            code += f'''parent=self.{ob.name.replace('.', '_')}'''



        #This has to be done every time the object updates:
        ob = ob.evaluated_get(dg) #this gives us the evaluated version of the object. Aka with all modifiers and deformations applied.
        mesh = ob.to_mesh() #turn it into the mesh data block we want.
        tris = []
        uvs = []
        vertex_colors = []

        for poly in mesh.polygons:
            tris.append(tuple(e for e in poly.vertices))

            uv_layer = mesh.uv_layers.active
            if uv_layer:
                for idx in poly.loop_indices:
                    uvs.append(tuple(uv_layer.data[idx].uv))

            color_layer = mesh.vertex_colors.active
            if color_layer:
                for idx in poly.loop_indices:
                    vertex_colors.append(tuple(color_layer.data[idx].color))

        code += f'''
    model=Mesh(
        vertices=[{', '.join([f'Vec3({v.co[0]}, {v.co[2]}, {v.co[1]})' for v in mesh.vertices])}],
        triangles={tris},'''

        code += f'''
        normals=({' ,'.join([f'Vec3({v.normal[0]}, {v.normal[2]}, {v.normal[1]})' for v in mesh.vertices])}),'''

        if uvs:
            code += f'''
        uvs={uvs},'''

        if vertex_colors:
            code += f'''
        colors={vertex_colors},'''

        code += '\n    )'
        code += '\n)'


        continue


        ob.select_set(state=True)
        bpy.context.view_layer.objects.active = ob
        #store object location then zero it out
        location = ob.location.copy()
        bpy.ops.object.location_clear()

        #export obj
        filename = path + scene_name+'.' + ob.name + '.obj'
        bpy.ops.export_scene.obj(filepath=filename, use_selection=True)

        #restore location
        ob.location = location

code += '''
if __name__ == '__main__':
    app = Ursina()
    EditorCamera()
    app.run()
'''
print(code)
with open(filepath, 'w') as f:
    f.write(code)
