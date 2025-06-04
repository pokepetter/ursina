from pathlib import Path
from ursina import application
from time import perf_counter
from ursina.string_utilities import print_info


def ursinamesh_to_obj(mesh, name='', out_path:Path=None, max_decimals=5, flip_faces=True):
    from ursina.string_utilities import camel_to_snake
    from ursina.array_tools import chunk_list


    if not name:
        name = camel_to_snake(mesh.__class__.__name__)

    obj = ''
    obj += f'mtllib {name}.mtl\n'
    obj += f'usemtl {name}\n'
    obj += f'o {name}\n'

    # Vertices
    for v in mesh.vertices:
        obj += f'v {round(v[0], max_decimals)} {round(v[1], max_decimals)} {round(v[2], max_decimals)}\n'

    # UVs
    has_uvs = bool(mesh.uvs)
    if has_uvs:
        for uv in mesh.uvs:
            obj += f'vt {round(uv[0], max_decimals)} {round(uv[1], max_decimals)}\n'

    # Normals
    has_normals = bool(mesh.normals)
    if has_normals:
        for n in mesh.normals:
            obj += f'vn {round(n[0], max_decimals)} {round(n[1], max_decimals)} {round(n[2], max_decimals)}\n'

    obj += 's off\n'

    # Triangles
    tris = mesh.triangles if mesh.triangles else chunk_list(mesh.indices, 3)

    for tri in tris:
        if flip_faces:
            tri = (tri[2], tri[1], tri[0])  # reverse winding

        obj += 'f'
        for idx in tri:
            v_idx = idx + 1  # OBJ is 1-indexed
            vt_idx = v_idx if has_uvs else ''
            vn_idx = v_idx if has_normals else ''

            if has_uvs and has_normals:
                obj += f' {v_idx}/{vt_idx}/{vn_idx}'
            elif has_uvs:
                obj += f' {v_idx}/{vt_idx}'
            elif has_normals:
                obj += f' {v_idx}//{vn_idx}'
            else:
                obj += f' {v_idx}'
        obj += '\n'

    out_file = out_path / f'{name}.obj'
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, 'w') as f:
        f.write(obj)

    print_info(f'saved obj: {out_file}')




def ursinamesh_to_dae(mesh, name, folder:Path=application.models_compressed_folder, texture_name=''):
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
    from ursina import Ursina, Entity, load_model, EditorCamera, Sky
    app = Ursina()

    t = perf_counter()
    Entity(model='untitled')
    print('-------', perf_counter() - t)
    m = load_model('cube', use_deepcopy=True)
    ursinamesh_to_dae(m, 'dae_export_test.dae')
    EditorCamera()
    Sky(texture='sky_sunset')

    app.run()
