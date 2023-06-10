import os
import glob
import platform
import subprocess
from copy import copy, deepcopy
from pathlib import Path
from ursina.mesh import Mesh
from ursina import application
from panda3d.core import CullFaceAttrib
from time import perf_counter
from ursina.string_utilities import print_info, print_warning
from ursina import color
from ursina.vec3 import Vec3


def ursinamesh_to_obj(mesh, name='', out_path=application.compressed_models_folder, max_decimals=5, flip_faces=True):
    from ursina.string_utilities import camel_to_snake

    obj = ''
    obj += f'mtllib {name}.mtl\n'
    obj += f'usemtl {name}\n'

    if not name:
        name = camel_to_snake(mesh.__class__.__name__)
    obj += 'o ' + name + '\n'
    verts = mesh.vertices

    for v in verts:
        v = [round(e, max_decimals) for e in v]
        obj += f'v {v[0]} {v[1]} {v[2]}\n'

    if mesh.uvs:
        for uv in mesh.uvs:
            uv = [round(e, max_decimals) for e in uv]
            obj += f'vt {uv[0]} {uv[1]}\n'

    obj += 's off\n'

    if mesh.triangles:
        tris = mesh.triangles

        if isinstance(tris[0], tuple): # convert from tuples to flat
            new_tris = []
            for t in tris:
                if len(t) == 3:
                    if not flip_faces:
                        new_tris.extend([t[0], t[1], t[2]])
                    else:
                        new_tris.extend([t[2], t[1], t[0]])
                elif len(t) == 4: # turn quad into tris
                    if not flip_faces:
                        new_tris.extend([t[0], t[1], t[2], t[2], t[3], t[0]])
                    else:
                        new_tris.extend([t[2], t[1], t[0], t[0], t[3], t[2]])

            tris = new_tris


    if mesh.mode == 'ngon':
        tris = []
        for i in range(1, len(mesh.vertices)-1):
            tris.extend((i, i+1, 0))


    # tris must be a list of indices
    for i, t in enumerate(tris):
        if i % 3 == 0:
            obj += '\nf '
        obj += str(t+1)
        if mesh.uvs:
            obj += '/'+str(t+1)
        obj += ' '

    obj += '\n'
    # print(obj)
    with open(out_path / (name + '.obj'), 'w') as f:
        f.write(obj)
        print_info('saved obj:', out_path / (name + '.obj'))





def ursinamesh_to_dae(mesh, name, folder:Path=application.compressed_models_folder, texture_name=''):
    num_vertices = len(mesh.generated_vertices)
    vertices = ' '.join([f'{v[2]} {v[1]} {v[0]}' for v in mesh.generated_vertices])

    # triangle_indices = ' '.join([f'{i} '*4 for i in range(num_vertices, 0, -1)])
    triangle_indices = ' '.join([f'{i} '*4 for i in range(num_vertices)])
    num_triangle_indices = num_vertices

    num_uvs = len(mesh.uvs)
    uvs = ' '.join([f'{uv[0]} {uv[1]}' for uv in mesh.uvs])

    num_vertex_colors = len(mesh.colors)
    vertex_colors = ' '.join([f'{c[0]} {c[1]} {c[2]} {c[3]}' for c in mesh.colors])

    texture_name = texture_name.replace('.','_')
    # print(vertices)
    text = f'''<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <asset>
    <contributor>
      <author>Ursina User</author>
      <authoring_tool>ursina</authoring_tool>
    </contributor>
    <unit name="meter" meter="1"/>
    <up_axis>Y_UP</up_axis>
  </asset>
  <library_effects>
    <effect id="Material-effect">
      <profile_COMMON>
        <newparam sid="{texture_name}-surface">
          <surface type="2D">
            <init_from>{texture_name}</init_from>
          </surface>
        </newparam>
        <newparam sid="{texture_name}-sampler">
          <sampler2D>
            <source>{texture_name}-surface</source>
          </sampler2D>
        </newparam>
        <technique sid="common">
          <lambert>
            <emission>
              <color sid="emission">0 0 0 1</color>
            </emission>
            <diffuse>
              <texture texture="{texture_name}-sampler" texcoord="UVMap"/>
            </diffuse>
            <index_of_refraction>
              <float sid="ior">1.45</float>
            </index_of_refraction>
          </lambert>
        </technique>
      </profile_COMMON>
    </effect>
  </library_effects>
  <library_images/>
  <library_materials>
    <material id="Material-material" name="Material">
      <instance_effect url="#Material-effect"/>
    </material>
  </library_materials>
  <library_geometries>
    <geometry id="Cube-mesh" name="Cube">
      <mesh>
        <source id="Cube-mesh-positions">
          <float_array id="Cube-mesh-positions-array" count="{num_vertices*3}">{vertices}</float_array>
          <technique_common>
            <accessor source="#Cube-mesh-positions-array" count="{num_vertices}" stride="3">
              <param name="X" type="float"/>
              <param name="Y" type="float"/>
              <param name="Z" type="float"/>
            </accessor>
          </technique_common>
        </source>
        <source id="Cube-mesh-normals">
          <float_array id="Cube-mesh-normals-array" count="18">0 0 1 0 -1 0 -1 0 0 0 0 -1 1 0 0 0 1 0</float_array>
          <technique_common>
            <accessor source="#Cube-mesh-normals-array" count="6" stride="3">
              <param name="X" type="float"/>
              <param name="Y" type="float"/>
              <param name="Z" type="float"/>
            </accessor>
          </technique_common>
        </source>
        <source id="Cube-mesh-map-0">
          <float_array id="Cube-mesh-map-0-array" count="{num_uvs*2}">{uvs}</float_array>
          <technique_common>
            <accessor source="#Cube-mesh-map-0-array" count="{num_uvs}" stride="2">
              <param name="S" type="float"/>
              <param name="T" type="float"/>
            </accessor>
          </technique_common>
        </source>
        <source id="Cube-mesh-colors-Col" name="Col">
          <float_array id="Cube-mesh-colors-Col-array" count="{num_vertex_colors*3}">{vertex_colors}</float_array>
          <technique_common>
            <accessor source="#Cube-mesh-colors-Col-array" count="{num_vertex_colors}" stride="4">
              <param name="R" type="float"/>
              <param name="G" type="float"/>
              <param name="B" type="float"/>
              <param name="A" type="float"/>
            </accessor>
          </technique_common>
        </source>
        <vertices id="Cube-mesh-vertices">
          <input semantic="POSITION" source="#Cube-mesh-positions"/>
        </vertices>
        <triangles material="Material-material" count="{num_triangle_indices}">
          <input semantic="VERTEX" source="#Cube-mesh-vertices" offset="0"/>
          <input semantic="NORMAL" source="#Cube-mesh-normals" offset="1"/>
          <input semantic="TEXCOORD" source="#Cube-mesh-map-0" offset="2" set="0"/>
          <input semantic="COLOR" source="#Cube-mesh-colors-Col" offset="3" set="0"/>
          <p>{triangle_indices}</p>
        </triangles>
      </mesh>
    </geometry>
  </library_geometries>
  <library_visual_scenes>
    <visual_scene id="Scene" name="Scene">
      <node id="Cube" name="Cube" type="NODE">
        <matrix sid="transform">1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1</matrix>
        <instance_geometry url="#Cube-mesh" name="Cube">
          <bind_material>
            <technique_common>
              <instance_material symbol="Material-material" target="#Material-material">
                <bind_vertex_input semantic="UVMap" input_semantic="TEXCOORD" input_set="0"/>
              </instance_material>
            </technique_common>
          </bind_material>
        </instance_geometry>
      </node>
    </visual_scene>
  </library_visual_scenes>
  <scene>
    <instance_visual_scene url="#Scene"/>
  </scene>
</COLLADA>
    '''
    with (folder / f'{name}.dae').open('w') as f:
        f.write(text)


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    t = perf_counter()
    Entity(model='untitled')
    print('-------', perf_counter() - t)
    m = load_model('cube', use_deepcopy=True)
    ursinamesh_to_dae(m, 'dae_export_test.dae')
    EditorCamera()
    Sky(texture='sky_sunset')

    app.run()
