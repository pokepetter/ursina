from ursina import *
from panda3d.core import MeshDrawer, NodePath
from panda3d.core import GeomVertexData, GeomVertexFormat, Geom, GeomNode
from panda3d.core import GeomTriangles, GeomTristrips, GeomTrifans
from panda3d.core import GeomLines, GeomLinestrips, GeomPoints
from panda3d.core import TexGenAttrib, TextureStage
from ursina.vec3 import Vec3
from ursina.scripts.generate_normals import generate_normals
from ursina.scripts.project_uvs import project_uvs
from ursina.scripts.colorize import colorize
from ursina import color
from ursina import application
from textwrap import dedent
from enum import Enum
from pathlib import Path

import array
import struct


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

# Create the vertex array data format
# vertex_format = GeomVertexArrayFormat("vertex", 3, core.Geom.NT_float32, core.Geom.C_point)
# normal_format = GeomVertexArrayFormat("normal", 3, core.Geom.NT_float32, core.Geom.NTFloat32)
# vertex_color_format = GeomVertexArrayFormat("color", 4, core.Geom.NT_uint8, core.Geom.C_color)
# uv_format = GeomVertexArrayFormat("uv", 2, core.Geom.NT_uint8, core.Geom.C_texcoord)


class FastMesh(NodePath):

    _formats = {
        (0,0,0) : GeomVertexFormat.getV3(),
        (1,0,0) : GeomVertexFormat.getV3c4(),
        (0,1,0) : GeomVertexFormat.getV3t2(),
        (0,0,1) : GeomVertexFormat.getV3n3(),
        (1,0,1) : GeomVertexFormat.getV3n3c4(),
        (1,1,0) : GeomVertexFormat.getV3c4t2(),
        (0,1,1) : GeomVertexFormat.getV3n3t2(),
        (1,1,1) : GeomVertexFormat.getV3n3c4t2(),
        }

    _modes = {
        'triangle' : GeomTriangles,
        'tristrip' : GeomTristrips,
        }

    def __init__(self, vertices=None, triangles=None, colors=None, uvs=None, normals=None, static=True, mode='triangle', thickness=1, render_points_in_3d=True):
        super().__init__('mesh')
        self.name = 'mesh'
        self.vertices = vertices
        self.triangles = triangles
        self.colors = colors
        self.uvs = uvs
        self.normals = normals
        self.static = static
        self.mode = mode
        self.thickness = thickness
        self.render_points_in_3d = render_points_in_3d

        # for var in (('vertices', vertices), ('triangles', triangles), ('colors', colors), ('uvs', uvs), ('normals', normals)):
        #     name, value = var
        #     if value is None:
        #         setattr(self, name, [])

        if self.vertices is not None:
            self.generate()


    def generate(self):  # call this after setting some of the variables to update it
        if hasattr(self, 'geomNode'):
            self.geomNode.removeAllGeoms()

        static_mode = Geom.UHStatic if self.static else Geom.UHDynamic
        vertex_format = Mesh._formats[(bool(self.colors), bool(self.uvs), bool(self.normals))]
        self.vdata = GeomVertexData('name', vertex_format, static_mode)
        self.vdata.setNumRows(len(self.vertices)//3) # for speed
        prim = Mesh._modes[self.mode](static_mode)

        vertices_array = self.vdata.modify_array(0)
        memview = memoryview(vertices_array).cast("B").cast("f")
        memview[:] = self.vertices

        # print(vertices_array)
        # arrayHandle0 = vertexData.modifyArray(0)
        # arrayHandle1 = vertexData.modifyArray(1)
        # arrayHandle0.modifyHandle().copyDataFrom(vertices.astype(np.float32))
        # arrayHandle1.modifyHandle().copyDataFrom(colors.astype(np.uint8))

        if not hasattr(self, 'geomNode'):
            self.geomNode = GeomNode('mesh')
            self.attachNewNode(self.geomNode)

        # self.generated_vertices = [self.vertices[i] for i in self.indices]
        # for i in len(self.vertices):
        #     prim.addVertex(v)

        # prim.addVertex((0,1,2))
        # prim.addVertex((3,4,5))
        [prim.addVertex(i) for i in range(len(self.vertices)//3)]

        prim.close_primitive()
        # print(prim)
        geom = Geom(self.vdata)
        geom.addPrimitive(prim)
        self.geomNode.addGeom(geom)




if __name__ == '__main__':
    from ursina import *

    app = Ursina()


    verts = ((0.5, 0.5, 0.0), (-0.5, 0.5, 0.0), (-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, -0.5, 0.0))
    sphere_model = load_model('sphere')
    verts = sphere_model.vertices
    norms =   sphere_model.normals

    flat_verts = []
    [flat_verts.extend(v) for v in verts]
    flat_verts = array.array("f", flat_verts)#.tobytes()

    flat_norms = []
    [flat_norms.extend(v) for v in norms]
    flat_norms = array.array("f", flat_norms)#.tobytes()

    # import numpy as np
    # verts = np.array(flat_verts, dtype=np.float32)

    from time import perf_counter

    t = perf_counter()
    fm = FastMesh(vertices=flat_verts)
    print('-------fast mesh:', perf_counter() - t)

    t = perf_counter()
    m = Mesh(vertices=flat_verts, fast=True)
    print('-------old mesh:', perf_counter() - t)

# -------fast mesh: 0.0006238999999998995
# -------old mesh: 0.0039017999999999553

    Entity(model=copy(fm), x=0)
    # Entity(model=copy(m), x=2)

    EditorCamera()
    app.run()
