from pathlib import Path
from enum import Enum
from textwrap import dedent
import numbers
import array

from ursina import application
from ursina import color
from ursina.scripts.generate_normals import generate_normals
from ursina.scripts.project_uvs import project_uvs
from ursina.scripts.colorize import colorize
from ursina.ursinastuff import LoopingList
from ursina.vec3 import Vec3
from ursina.vec2 import Vec2
from ursina.sequence import Func

import panda3d.core as p3d

class MeshModes(Enum):
    triangle = 'triangle'
    ngon = 'ngon'
    quad = 'quad'
    line = 'line'
    point = 'point'
    tristrip = 'tristrip'

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other): # overridden __eq__ to allow for both str and MeshModes comparisons
        if isinstance(other, MeshModes):
            return self.value == other.value
        return self.value == other



class Mesh(p3d.NodePath):
    _modes = {
        'triangle' : p3d.GeomTriangles,
        'tristrip' : p3d.GeomTristrips,
        'ngon' : p3d.GeomTrifans,
        'line' : p3d.GeomLinestrips,
        'point' : p3d.GeomPoints,
    }

    def __init__(self, vertices=None, triangles=None, colors=None, uvs=None, normals=None, static=True, mode='triangle', thickness=1, render_points_in_3d=True, vertex_buffer=None, vertex_buffer_length=None, vertex_buffer_format=None):
        super().__init__('mesh')
        self.vertices = vertices
        self.triangles = triangles
        self.colors = colors
        self.uvs = uvs
        self.normals = normals
        self.static = static
        self.mode = mode
        self.thickness = thickness
        self.render_points_in_3d = render_points_in_3d
        self.vertex_buffer = vertex_buffer
        self.vertex_buffer_length = vertex_buffer_length
        self.vertex_buffer_format = vertex_buffer_format

        self._generated_vertices = None

        for var in (('vertices', vertices), ('triangles', triangles), ('colors', colors), ('uvs', uvs), ('normals', normals)):
            name, value = var
            if value is None:
                setattr(self, name, [])

        if (self.vertices is not None and len(self.vertices) > 0) or self.vertex_buffer is not None:
            self.generate()


    def _ravel(self, data):
        if not isinstance(data[0], numbers.Real):
            d = []
            for v in data:
                d.extend(v)
            return d
        return data


    def _set_array_data(self, array_handle, data, dtype_string='f'):
        a = None
        try:
            a = memoryview(data).cast('B').cast(dtype_string)
        except:
            a = array.array(dtype_string, data)

        vmem = memoryview(array_handle).cast('B').cast(dtype_string)
        try:
            vmem[:] = a
        except:
            raise Exception(f'Error in Mesh. Ensure Mesh is valid and the inputs have same length: vertices:{len(self.vertices)}, triangles:{len(self.triangles)}, normals:{len(self.normals)}, colors:{len(self.colors)}, uvs:{len(self.uvs)}')

    def generate(self):
        self._generated_vertices = None

        if hasattr(self, 'geomNode'):
            self.geomNode.removeAllGeoms()
        else:
            self.geomNode = p3d.GeomNode('mesh_geom')
            self.attachNewNode(self.geomNode)

        if len(self.vertices) == 0 and self.vertex_buffer is None:
            return

        static_mode = p3d.Geom.UHStatic if self.static else p3d.Geom.UHDynamic
        vertex_format = p3d.GeomVertexFormat()

        color_attribute_index = -1
        uv_attribute_index = -1
        normal_attribute_index = -1

        if self.vertex_buffer is not None:
            vertex_array_format = p3d.GeomVertexArrayFormat()
            attributes = self.vertex_buffer_format.split(",")
            for attribute in attributes:
                attribute_type = attribute[0]
                attribute_type_name = attribute[0]
                if attribute_type == "p":
                    attribute_type = p3d.Geom.C_point
                    attribute_type_name = "vertex"
                elif attribute_type == "c":
                    attribute_type = p3d.Geom.C_color
                    attribute_type_name = "color"
                elif attribute_type == "t":
                    attribute_type = p3d.Geom.C_texcoord
                    attribute_type_name = "texcoord"
                elif attribute_type == "n":
                    attribute_type = p3d.Geom.C_normal
                    attribute_type_name = "normal"
                else:
                    raise Exception("Invalid vertex buffer format attribute type: {}.".format(attribute_type))
                attribute_count = int(attribute[1:-1])
                attribute_dtype = attribute[-1]
                if attribute_dtype == "f":
                    attribute_dtype = p3d.Geom.NT_float32
                elif attribute_dtype == "I":
                    attribute_dtype = p3d.Geom.NT_uint32
                else:
                    raise Exception("Invalid vertex buffer format attribute data type: {}.".format(attribute_dtype))
                vertex_array_format.addColumn(attribute_type_name, attribute_count, attribute_dtype, attribute_type)
            vertex_format.addArray(vertex_array_format)

        else:
            vertex_format = p3d.GeomVertexFormat()
            vertex_format.add_array(p3d.GeomVertexFormat.getV3().arrays[0])
            attribute_count = 1
            if self.colors is not None and len(self.colors) > 0:
                vertex_format.add_array(p3d.GeomVertexArrayFormat('color', 4, p3d.Geom.NT_float32, p3d.Geom.C_color))
                color_attribute_index = attribute_count
                attribute_count += 1
            if self.uvs is not None and len(self.uvs) > 0 and self.mode not in ['line', 'point']:
                vertex_format.add_array(p3d.GeomVertexArrayFormat('texcoord', 2, p3d.Geom.NT_float32, p3d.Geom.C_texcoord))
                uv_attribute_index = attribute_count
                attribute_count += 1
            if self.normals is not None and len(self.normals) > 0 and self.mode not in ['line', 'point']:
                vertex_format.add_array(p3d.GeomVertexArrayFormat('normal', 3, p3d.Geom.NT_float32, p3d.Geom.C_normal))
                normal_attribute_index = attribute_count
                attribute_count += 1

        vertex_format = p3d.GeomVertexFormat.register_format(vertex_format)
        vdata = p3d.GeomVertexData('vertex_data', vertex_format, static_mode)

        if self.vertex_buffer is not None:
            m = memoryview(self.vertex_buffer).cast('B')
            vdata.unclean_set_num_rows(self.vertex_buffer_length)
            array_handle = vdata.modify_array(0)
            vmem = memoryview(array_handle).cast('B')
            vmem[:] = m

        else:
            if isinstance(self.vertices[0], numbers.Real):
                vdata.unclean_set_num_rows(len(self.vertices) // 3)
            else:
                vdata.unclean_set_num_rows(len(self.vertices))

            self._set_array_data(vdata.modify_array(0), self._ravel(self.vertices), 'f')

            if self.colors is not None and len(self.colors) > 0:
                self._set_array_data(vdata.modify_array(color_attribute_index), self._ravel(self.colors), 'f')

            if self.uvs is not None and len(self.uvs) > 0 and self.mode not in ['line', 'point']:
                self._set_array_data(vdata.modify_array(uv_attribute_index), self._ravel(self.uvs), 'f')

            if self.normals is not None and len(self.normals) > 0 and self.mode not in ['line', 'point']:
                self._set_array_data(vdata.modify_array(normal_attribute_index), self._ravel(self.normals), 'f')

        geom = p3d.Geom(vdata)

        if len(self.triangles) == 0:    # no triangles provided, so just add them in order
            prim = Mesh._modes[self.mode](static_mode)
            prim.set_index_type(p3d.GeomEnums.NT_uint32)

            parray = prim.modify_vertices()
            n = len(self.vertices)
            if isinstance(self.vertices[0], numbers.Real):
                n = n // 3
            triangles = [i for i in range(n)]
            parray.unclean_set_num_rows(n)
            self._set_array_data(parray, triangles, 'I')

            prim.close_primitive()
            geom.addPrimitive(prim)

        else:
            if not isinstance(self.triangles[0], numbers.Real): # triangles provided as [(0,1,2), (3,4,5,6), ...] etc., so unpack them
                line_segments = []
                indices = self.indices
                for tup in self.triangles:
                    if len(tup) == 2:
                        line_segments.append(tup)


                for line_segment in line_segments:
                    prim = Mesh._modes['line'](static_mode)
                    prim.set_index_type(p3d.GeomEnums.NT_uint32)
                    parray = prim.modify_vertices()
                    parray.unclean_set_num_rows(len(line_segment))
                    self._set_array_data(parray, line_segment, 'I')
                    prim.close_primitive()
                    geom.addPrimitive(prim)

                if len(indices) > 0:
                    prim = Mesh._modes[self.mode](static_mode)
                    prim.set_index_type(p3d.GeomEnums.NT_uint32)
                    parray = prim.modify_vertices()
                    parray.unclean_set_num_rows(len(indices))
                    self._set_array_data(parray, indices, 'I')
                    prim.close_primitive()
                    geom.addPrimitive(prim)

            else:   # got triangles as [0,1,2,3,4,5], ie. flat
                prim = Mesh._modes[self.mode](static_mode)
                prim.set_index_type(p3d.GeomEnums.NT_uint32)

                parray = prim.modify_vertices()

                parray.unclean_set_num_rows(len(self.triangles))
                self._set_array_data(parray, self._ravel(self.triangles), 'I')

                prim.close_primitive()
                geom.addPrimitive(prim)

        self.geomNode.addGeom(geom)

        if self.mode == 'point':
            self.setTexGen(p3d.TextureStage.getDefault(), p3d.TexGenAttrib.MPointSprite)


    @property
    def indices(self):
        if not self.triangles:
            return list(range(len(self.vertices)))

        if self.triangles and isinstance(self.triangles[0], numbers.Real):
            return self.triangles

        indices = []
        for tup in self.triangles:
            # if len(tup) == 2:
            #     line_segments.append(tup)
            if len(tup) == 3:
                indices.extend(tup)
            elif len(tup) == 4:
                indices.extend((tup[0], tup[1], tup[2],
                                  tup[2], tup[3], tup[0]))
            elif len(tup) > 4:
                tup = LoopingList(tup)
                for i in range(1, len(tup)):
                    indices.extend((tup[0], tup[i], tup[i+1]))

        return indices


    @property
    def generated_vertices(self):
        if self._generated_vertices is None:
            if self.triangles is not None and len(self.triangles) > 0:
                if not isinstance(self.triangles[0], numbers.Real):
                    tris = []
                    for tup in self.triangles:
                        if len(tup) == 4:
                            tris.extend((tup[0], tup[1], tup[2],
                                         tup[2], tup[3], tup[0]))
                        else:
                            tris.extend(tup)
                    self._generated_vertices = [self.vertices[i] for i in tris]
                else:
                    self._generated_vertices = [self.vertices[i] for i in self.triangles]
            else:
                self._generated_vertices = self.vertices
        return self._generated_vertices

    @generated_vertices.setter
    def generated_vertices(self, value):
        self._generated_vertices = value

    @property
    def recipe(self):
        if hasattr(self, '_recipe'):
            return self._recipe

        vbuf_format = self.vertex_buffer_format
        if vbuf_format is not None:
            vbuf_format = f'"{vbuf_format}"'

        return dedent(f'''
            Mesh(
                vertices={[tuple(e) for e in self.vertices]},
                triangles={self.triangles},
                colors={[tuple(e) for e in self.colors]},
                uvs={[tuple(e) for e in self.uvs]},
                normals={[tuple(e) for e in self.normals]},
                static={self.static},
                mode="{self.mode}",
                thickness={self.thickness},
                render_points_in_3d={self.render_points_in_3d},
                vertex_buffer={self.vertex_buffer},
                vertex_buffer_length={self.vertex_buffer_length},
                vertex_buffer_format={vbuf_format}
            )
        ''')


    @property
    def render_points_in_3d(self):
        return self._render_points_in_3d

    @render_points_in_3d.setter
    def render_points_in_3d(self, value):
        self._render_points_in_3d = value
        self.set_render_mode_perspective(value)

    def __repr__(self):
        if not self.name == 'mesh':
            return self.name
        else:
            return self.recipe

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name

    def __add__(self, other):
        if self.vertex_buffer is not None:
            raise Exception("Can't add mesh with vertex buffer to another mesh (operation not supported).")

        self.vertices += other.vertices
        self.triangles += other.triangles
        if other.colors:
            self.colors += other.colors
        else:
            self.colors += (color.white, ) * len(other.vertices)
        self.normals += other.normals
        self.uvs += other.uvs

    def __deepcopy__(self, memo):
        m = Mesh(
            vertices=[Vec3(*e) for e in self.vertices],
            triangles=self.triangles,
            colors=[Color(*e) for e in self.colors],
            uvs=[Vec2(*e) for e in self.uvs],
            normals=[Vec3(*e) for e in self.normals],
            static=self.static,
            mode=self.mode,
            thickness=self.thickness,
            render_points_in_3d=self.render_points_in_3d,
            vertex_buffer=self.vertex_buffer,
            vertex_buffer_length=self.vertex_buffer_length,
            vertex_buffer_format=self.vertex_buffer_format
        )
        m.name = self.name
        return m

    @property
    def thickness(self):
        return self.getRenderModeThickness()

    @thickness.setter
    def thickness(self, value):
        self.setRenderModeThickness(value)

    def generate_normals(self, smooth=True, regenerate=True):
        self.normals = list(generate_normals(self.vertices, self.triangles, smooth))
        if regenerate:
            self.generate()
        return self.normals

    def colorize(self, left=color.white, right=color.blue, down=color.red, up=color.green, back=color.white, forward=color.white, smooth=True, world_space=True, strength=1):
        colorize(self, left, right, down, up, back, forward, smooth, world_space, strength)

    def project_uvs(self, aspect_ratio=1, direction='forward'):
        project_uvs(self, aspect_ratio)

    def clear(self, regenerate=True):
        if self.vertex_buffer is not None:
            self.vertex_buffer = None
            self.vertex_buffer_length = None
            self.vertex_buffer_format = None
        self.vertices = []
        self.triangles = []
        self.colors = []
        self.uvs = []
        self.normals = []
        if regenerate:
            self.generate()

    def save(self, name='', folder:Path=Func(getattr, application, 'compressed_models_folder'), flip_faces=False, max_decimals=16):
        if callable(folder):
            folder = folder()
        if not folder.exists():
            folder.mkdir()

        if not name and hasattr(self, 'path'):
            name = self.path.stem
            if '.' not in name:
                name += '.ursinamesh'

        if name.endswith('ursinamesh'):
            mesh_code = dedent(f'''
            Mesh(
                vertices={[tuple(round(_,max_decimals) for _ in e) for e in self.vertices]},
                triangles={self.triangles},
                colors={[tuple(round(_,max_decimals) for _ in e) for e in self.colors]},
                uvs={[tuple(round(_,max_decimals) for _ in e) for e in self.uvs]},
                normals={[tuple(round(_,max_decimals) for _ in e) for e in self.normals]},
                static={self.static},
                mode="{self.mode}",
                thickness={self.thickness},
                render_points_in_3d={self.render_points_in_3d},
            )'''[1:])
            with open(folder / name, 'w') as f:
                f.write(mesh_code)
            print('saved .ursinamesh to:', folder / name)


        elif name.endswith('.obj'):
            from ursina.mesh_exporter import ursinamesh_to_obj
            import os
            name = str(os.path.splitext(name)[0])
            ursinamesh_to_obj(self, name, folder, flip_faces)
        elif name.endswith('.dae'):
            from ursina.mesh_exporter import ursinamesh_to_dae
            import os
            name = str(os.path.splitext(name)[0])
            ursinamesh_to_dae(self, name, folder)
        elif name.endswith('.bam'):
            self.writeBamFile(folder / name)
            print('saved .bam to:', folder / name)


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    # verts as list of tuples
    e = Entity(position=(0,0), model=Mesh(vertices=[(-.5,0,0), (.5,0,0), (0, 1, 0)]))

    # verts as tuple of tuples
    e = Entity(position=(1,0), model=Mesh(vertices=((-.5,0,0), (.5,0,0), (0, 1, 0))))
    Text(parent=e, text='triangle mesh\nwith verts as tuple of tuples', y=1, scale=5, origin=(0,-.5))

    # verts as list of lists
    e = Entity(position=(0,-2), model=Mesh(vertices=[[-.5,0,0], [.5,0,0], [0, 1, 0]]))
    Text(parent=e, text='triangle mesh\nwith verts as list of lists', y=1, scale=5, origin=(0,-.5))

    # verts as tuple of lists
    e = Entity(position=(1,-2), model=Mesh(
        vertices=([-.5,0,0], [.5,0,0], [0, 1, 0])
    ))
    Text(parent=e, text='triangle mesh\nwith verts as tuple of lists', y=1, scale=5, origin=(0,-.5))

    # verts as list Vec3
    e = Entity(position=(0,-4), model=Mesh(
        vertices=[Vec3(-.5,0,0), Vec3(.5,0,0), Vec3(0, 1, 0)],
    ))
    Text(parent=e, text='triangle mesh\nwith verts as list Vec3', y=1, scale=5, origin=(0,-.5))


    # tris as flat list
    e = Entity(position=(1,-4), model=Mesh(
        vertices=[Vec3(-.5,0,0), Vec3(.5,0,0), Vec3(0, 1, 0)],
        triangles = [0,1,2],
    ))
    Text(parent=e, text='triangle mesh\nwith tris as flat list', y=1, scale=5, origin=(0,-.5))

    # tris as list of triangles
    e = Entity(position=(2.5,0), model=Mesh(
        vertices=[Vec3(-.5,0,0), Vec3(.5,0,0), Vec3(0, 1, 0)],
        triangles = [(0,1,2), (2,1,0)], # should be double sided
    ))
    Text(parent=e, text='triangle mesh\nwith tris as list of triangles', y=1, scale=5, origin=(0,-.5))


    continious_line = Entity(position=(4,0), model=Mesh(
        vertices=(Vec3(0,0,0), Vec3(.6,.3,0), Vec3(1,1,0), Vec3(.6,1.7,0), Vec3(0,2,0)),
        # triangles= ((0,1), (3,4,5)),
        mode='line',
        thickness=4,
        ), color=color.cyan)
    Text(parent=continious_line, text='continious_line', y=1, scale=5)

    line_segments = Entity(position=(4,-2), model=Mesh(
        vertices=(Vec3(0,0,0), Vec3(.6,.3,0), Vec3(1,1,0), Vec3(.6,1.7,0), Vec3(0,2,0)),
        triangles= ((0,1), (3,4)),
        mode='line',
        thickness=4,
        ), color=color.magenta)
    Text(parent=line_segments, text='line_segments', y=1, scale=5)

    points = Entity(position=(6,0), model=Mesh(vertices=(Vec3(0,0,0), Vec3(.6,.3,0), Vec3(1,1,0), Vec3(.6,1.7,0), Vec3(0,2,0)), mode='point', thickness=.05), color=color.red)
    Text(parent=points, text='points', y=1, scale=5)

    points_2d = Entity(position=(6,-2), model=Mesh(vertices=(Vec3(0,0,0), Vec3(.6,.3,0), Vec3(1,1,0), Vec3(.6,1.7,0), Vec3(0,2,0)), mode='point', thickness=10, render_points_in_3d=False), color=color.red)
    Text(parent=points_2d, text='points_2d', y=1, scale=5)

    quad = Entity(
        position=(8,0),
        model=Mesh(
            vertices=((0.5, 0.5, 0.0), (-0.5, 0.5, 0.0), (-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, -0.5, 0.0)),
            uvs=((1, 1), (0, 1), (0, 0), (1, 0), (1, 1), (0, 0)),
            mode='triangle'),
        texture='shore'
        )
    Text(parent=quad, text='quad_with_uvs', y=1, scale=5, origin=(0,-.5))

    quad = Entity(
        position=(8,-2),
        model=Mesh(
            vertices=((0.5, 0.5, 0.0), (-0.5, 0.5, 0.0), (-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, -0.5, 0.0)),
            uvs=((1, 1), (0, 1), (0, 0), (1, 0), (1, 1), (0, 0)),
            normals=[(-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0)],
            mode='triangle'),
        )
    Text(parent=quad, text='quad_with_normals', y=1, scale=5, origin=(0,-.5))

    quad = Entity(
        position=(8,-4),
        model=Mesh(
            vertices=((0.5, 0.5, 0.0), (-0.5, 0.5, 0.0), (-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, -0.5, 0.0)),
            uvs=((1, 1), (0, 1), (0, 0), (1, 0), (1, 1), (0, 0)),
            normals=[(-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0)],
            mode='triangle'),
        )
    Text(parent=quad, text='quad_with_usv_and_normals', y=1, scale=5, origin=(0,-.5))

    quad = Entity(
        position=(8,-6),
        model=Mesh(
            vertices=((0.5, 0.5, 0.0), (-0.5, 0.5, 0.0), (-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, -0.5, 0.0)),
            uvs=((1, 1), (0, 1), (0, 0), (1, 0), (1, 1), (0, 0)),
            normals=[(-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, -1.0)],
            colors=[color.red, color.yellow, color.green, color.cyan, color.blue, color.magenta],
            mode='triangle'),
        )
    Text(parent=quad, text='quad_with_usv_and_normals_and_vertex_colors', y=1, scale=5, origin=(0,-.5))

    quad = Entity(
        position=(10,0),
        model=Mesh(
            vertices=((-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, 0.5, 0.0)),
            triangles=(0,1,2, 2,3,0),
            mode='triangle'),
        )
    Text(parent=quad, text='triangles flat', y=1, scale=5, origin=(0,-.5))

    quad = Entity(
        position=(10,-2),
        model=Mesh(
            vertices=((-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, 0.5, 0.0)),
            triangles=((0,1,2), (2,3,0)),
            mode='triangle'),
        )
    Text(parent=quad, text='triangles triplets', y=1, scale=5, origin=(0,-.5))

    quad = Entity(
        position=(10,-4),
        model=Mesh(
            vertices=((-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, 0.5, 0.0)),
            triangles=((0,1,2,3), (0,3,2)),
            mode='triangle'),
        )
    Text(parent=quad, text='triangles quad + tri', y=1, scale=5, origin=(0,-.5))

    copy_test = Entity(position=(12,0), model=copy(quad.model))
    Text(parent=copy_test, text='copy_test', y=1, scale=5, origin=(0,-.5))

    deepcopy_test = Entity(position=(12,-2), model=deepcopy(quad.model))
    Text(parent=deepcopy_test, text='deepcopy_test', y=1, scale=5, origin=(0,-.5))

    clear_test = Entity(position=(12,-4), model=deepcopy(quad.model))
    clear_test.model.clear()
    Text(parent=clear_test, text='.clear() test', y=1, scale=5, origin=(0,-.5))

    recipe_test = Entity(position=(12,-6), model=eval(quad.model.recipe))
    Text(parent=recipe_test, text='.recipe test', y=1, scale=5, origin=(0,-.5))

    window.color = color.black
    EditorCamera()

    app.run()
