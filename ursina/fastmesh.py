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
        #         setattr(self, name, list())

        if self.vertices is not None:
            self.generate()


    def generate(self):  # call this after setting some of the variables to update it
        if hasattr(self, 'geomNode'):
            self.geomNode.removeAllGeoms()

        # prim.modify_vertices()

        static_mode = Geom.UHStatic if self.static else Geom.UHDynamic
        vertex_format = Mesh._formats[(bool(self.colors), bool(self.uvs), bool(self.normals))]
        self.vdata = GeomVertexData('name', vertex_format, static_mode)
        self.vdata.setNumRows(len(self.vertices)//3) # for speed

        arrayHandle0: core.GeomVertexArrayData = self.vdata.modifyArray(0)
        # arrayHandle1: core.GeomVertexArrayData = self.vdata.modifyArray(1)
        prim = Mesh._modes[self.mode](static_mode)
        # coords = [1., -3., 7., -4., 12., 5., 8., 2., -1., -6., 14., -11.]
        # either convert this sequence to an array of bytes...
        # (note that if you call tobytes() on it, you don't need to call
        # cast("f") on the memoryview, below)
        # pos_data = array.array("f", self.vertices)#.tobytes()


        pos_array = self.vdata.modify_array(0)
        memview = memoryview(pos_array).cast("B").cast("f")
        # memview = memoryview(pos_array).cast("B")
        memview[:] = self.vertices
        # print(pos_array)

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
    verts = load_model('sphere').vertices

    flat_verts = []
    [flat_verts.extend(v) for v in verts]
    flat_verts = array.array("f", flat_verts)#.tobytes()

    from time import perf_counter

    t = perf_counter()
    fm = FastMesh(vertices=flat_verts)
    print('-------fast mesh:', perf_counter() - t)

    t = perf_counter()
    m = Mesh(vertices=verts)
    print('-------old mesh:', perf_counter() - t)

    Entity(model=copy(fm), x=0)
    Entity(model=copy(m), x=2)

    EditorCamera()
    app.run()
