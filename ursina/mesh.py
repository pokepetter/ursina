from pathlib import Path
from enum import Enum
from textwrap import dedent
import struct
import numbers
import array

from ursina import application
from ursina import color
from ursina.scripts.generate_normals import generate_normals
from ursina.scripts.project_uvs import project_uvs
from ursina.scripts.colorize import colorize

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

    def __eq__(self, other):
        # overridden __eq__ to allow for both str and InputEvent comparisons
        if isinstance(other, MeshModes):
            return self.value == other.value
        return self.value == other


class Mesh(p3d.NodePath):
    _formats = {
        (0,0,0) : p3d.GeomVertexFormat.getV3(),
        (1,0,0) : p3d.GeomVertexFormat.getV3c4(),
        (0,1,0) : p3d.GeomVertexFormat.getV3t2(),
        (0,0,1) : p3d.GeomVertexFormat.getV3n3(),
        (1,0,1) : p3d.GeomVertexFormat.getV3n3c4(),
        (1,1,0) : p3d.GeomVertexFormat.getV3c4t2(),
        (0,1,1) : p3d.GeomVertexFormat.getV3n3t2(),
        (1,1,1) : p3d.GeomVertexFormat.getV3n3c4t2(),
    }

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

        for var in (('vertices', vertices), ('triangles', triangles), ('colors', colors), ('uvs', uvs), ('normals', normals)):
            name, value = var
            if value is None:
                setattr(self, name, [])

        if self.vertices != [] or self.vertex_buffer is not None:
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
        vmem[:] = a

    def generate(self):
        if hasattr(self, 'geomNode'):
            self.geomNode.removeAllGeoms()
        else:
            self.geomNode = p3d.GeomNode('mesh_geom')
            self.attachNewNode(self.geomNode)

        if len(self.vertices) == 0 and self.vertex_buffer is None:
            return

        static_mode = p3d.Geom.UHStatic if self.static else p3d.Geom.UHDynamic

        vertex_format = p3d.GeomVertexFormat()

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
            if self.colors is not None and len(self.colors) > 0:
                vertex_format.add_array(p3d.GeomVertexArrayFormat('color', 4, p3d.Geom.NT_float32, p3d.Geom.C_color))
            if self.uvs is not None and len(self.uvs) > 0:
                vertex_format.add_array(p3d.GeomVertexArrayFormat('texcoord', 2, p3d.Geom.NT_float32, p3d.Geom.C_texcoord))
            if self.normals is not None and len(self.normals) > 0:
                vertex_format.add_array(p3d.GeomVertexArrayFormat('normal', 3, p3d.Geom.NT_float32, p3d.Geom.C_normal))

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
                self._set_array_data(vdata.modify_array(1), self._ravel(self.colors), 'f')

            if self.uvs is not None and len(self.uvs) > 0:
                self._set_array_data(vdata.modify_array(2), self._ravel(self.uvs), 'f')

            if self.normals is not None and len(self.normals) > 0:
                self._set_array_data(vdata.modify_array(3), self._ravel(self.normals), 'f')

        prim = Mesh._modes[self.mode](static_mode)
        prim.set_index_type(p3d.GeomEnums.NT_uint32)

        parray = prim.modify_vertices()
        parray.unclean_set_num_rows(len(self.triangles))

        if not isinstance(self.triangles[0], numbers.Real) and len(self.triangles[0]) == 4:
            tris = bytearray()
            for quad in self.triangles:
                tris.extend(struct.pack(
                    "6I",
                    quad[0], quad[1], quad[2],
                    quad[2], quad[3], quad[0]
                ))
            self._set_array_data(parray, tris, 'I')
        else:
            self._set_array_data(parray, self._ravel(self.triangles), 'I')

        prim.close_primitive()

        geom = p3d.Geom(vdata)
        geom.addPrimitive(prim)
        self.geomNode.addGeom(geom)

        if self.mode == 'point':
            self.setTexGen(p3d.TextureStage.getDefault(), p3d.TexGenAttrib.MPointSprite)

    @property
    def generated_vertices(self):
        if not hasattr(self, "_generated_vertices"):
            if self.triangles is not None and len(self.triangles) > 0:
                return [self.vertices[i] for i in self.triangles]
            else:
                return [v for v in self.vertices]
        return self._generated_vertices

    @generated_vertices.setter
    def generated_vertices(self, value):
        self._generated_vertices = value

    @property
    def recipe(self):
        if hasattr(self, '_recipe'):
            return self._recipe

        return dedent(f'''
            Mesh(
                vertices={list(self.vertices)},
                triangles={list(self.triangles)},
                colors={list(self.colors)},
                uvs={list(self.uvs)},
                normals={list(self.normals)},
                static={self.static},
                mode="{self.mode}",
                thickness={self.thickness},
                render_points_in_3d={self.render_points_in_3d},
                vertex_buffer={self.vertex_buffer},
                vertex_buffer_length={self.vertex_buffer_length},
                vertex_buffer_format="{self.vertex_buffer_format}"
            )
        ''')

    @recipe.setter
    def recipe(self, value):
        self._recipe = value

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
            vertices=self.vertices,
            triangles=self.triangles,
            colors=self.colors,
            uvs=self.uvs,
            normals=self.normals,
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

    @property
    def triangles(self):
        if self._triangles is None:
            if self.mode == 'line':
                self._triangles = [(i, i + 1) for i in range(0, len(self.vertices), 2)]
            else:
                self._triangles = [(i, i + 1, i + 2) for i in range(0, len(self.vertices), 3)]

        return self._triangles

    @triangles.setter
    def triangles(self, value):
        self._triangles = value

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

    def save(self, name='', folder:Path=application.compressed_models_folder, flip_faces=False):
        if not application.compressed_models_folder.exists():
            application.compressed_models_folder.mkdir()

        if not name and hasattr(self, 'path'):
            name = self.path.stem
            if '.' not in name:
                name += ".ursinamesh"

        if name.endswith('ursinamesh'):
            with open(folder / name, 'w') as f:
                f.write(self.recipe)
            print('saved .ursinamesh to:', folder / name)
        elif name.endswith('.obj'):
            from ursina.mesh_exporter import ursinamesh_to_obj
            import os
            name = str(os.path.splitext(name)[0])
            ursinamesh_to_obj(self, name, folder, flip_faces)
        elif name.endswidth('.dae'):
            from ursina.mesh_exporter import ursinamesh_to_dae
            import os
            name = str(os.path.splitext(name)[0])
            ursinamesh_to_dae(self, name, folder)
        elif name.endswith('.bam'):
            success = self.writeBamFile(folder / name)
            print('saved .bam to:', folder / name)


if __name__ == '__main__':
    from ursina import *

    app = Ursina()

    verts = ((0,0,0), (1,0,0), (.5, 1, 0), (-.5,1,0))
    tris = (1, 2, 0, 2, 3, 0)
    uvs = ((1.0, 0.0), (0.0, 1.0), (0.0, 0.0), (1.0, 1.0))
    norms = ((0,0,-1),) * len(verts)
    colors = (color.red, color.blue, color.lime, color.black)


    e = Entity(model=Mesh(vertices=verts, triangles=tris, uvs=uvs, normals=norms, colors=colors), scale=2)
    # line mesh test
    verts = (Vec3(0,0,0), Vec3(0,1,0), Vec3(1,1,0), Vec3(2,2,0), Vec3(0,3,0), Vec3(-2,3,0))
    tris = ((0,1), (3,4,5))

    lines = Entity(model=Mesh(vertices=verts, triangles=tris, mode='line', thickness=4), color=color.cyan, z=-1)
    points = Entity(model=Mesh(vertices=verts, mode='point', thickness=.05), color=color.red, z=-1.01)
    # points.model.mode = MeshModes.point     # can also use the MeshMode enum
    # print(e.model.recipe)
    # e.model.save('bam_test', application.compressed_models_folder, 'bam')

    # test
    # from time import perf_counter
    # e = Entity(model=Mesh(vertices=[Vec3(0,0,0), Vec3(1,0,0), Vec3(.5,1,0)]))
    # for i in range(3):
    #     clone = Entity(model=deepcopy(e.model),x=i)
    #
    # clone.model.vertices = [v+Vec3(0,-2,0) for v in clone.model.vertices]
    # t = perf_counter()
    # clone.model.generate()
    # print('-------', (perf_counter() - t) * 1000)
    # print(clonde.mode)

    # test .clear()
    e.model.clear()
    points.model.clear()
    lines.model.clear()
    EditorCamera()
    app.run()
