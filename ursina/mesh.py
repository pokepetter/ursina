from panda3d.core import MeshDrawer, NodePath
from panda3d.core import GeomVertexData, GeomVertexFormat, Geom, GeomVertexWriter, GeomNode
from panda3d.core import GeomTriangles, GeomTristrips, GeomTrifans
from panda3d.core import GeomLines, GeomLinestrips, GeomPoints
from ursina.scripts.generate_normals import generate_normals
from ursina.scripts.project_uvs import project_uvs
from ursina.scripts.colorize import colorize
from ursina import color


class Mesh(NodePath):

    def __init__(self, vertices=None, triangles=None, colors=None, uvs=None, normals=None, static=True, mode='triangle', thickness=1):
        super().__init__('mesh')

        self.vertices = vertices
        self._triangles = triangles
        self.colors = colors
        self.uvs = uvs
        self.normals = normals
        self.static = static
        self.mode = mode
        self.thickness = thickness

        if self.vertices:
            self.vertices = [tuple(v) for v in self.vertices]
            self.generate()


    def generate(self):  # call this after setting some of the variables to update it
        if not self.vertices:
            return

        if hasattr(self, 'geomNode'):
            self.geomNode.removeAllGeoms()

        static_mode = Geom.UHStatic if self.static else Geom.UHDynamic

        formats = {
            (0,0,0) : GeomVertexFormat.getV3(),
            (1,0,0) : GeomVertexFormat.getV3c4(),
            (0,1,0) : GeomVertexFormat.getV3t2(),
            (0,0,1) : GeomVertexFormat.getV3n3(),
            (1,0,1) : GeomVertexFormat.getV3n3c4(),
            (1,1,0) : GeomVertexFormat.getV3c4t2(),
            (0,1,1) : GeomVertexFormat.getV3n3t2(),
            (1,1,1) : GeomVertexFormat.getV3n3c4t2(),
            }

        vertex_format = formats[(bool(self.colors), bool(self.uvs), bool(self.normals))]
        vdata = GeomVertexData('name', vertex_format, static_mode)
        vdata.setNumRows(len(self.vertices)) # for speed


        vertexwriter = GeomVertexWriter(vdata, 'vertex')
        for v in self.vertices:
            vertexwriter.addData3f((v[0], v[2], v[1])) # swap y and z

        if self.colors:
            colorwriter = GeomVertexWriter(vdata, 'color')
            for c in self.colors:
                colorwriter.addData4f(c)

        if self.uvs:
            uvwriter = GeomVertexWriter(vdata, 'texcoord')
            for uv in self.uvs:
                uvwriter.addData2f(uv[0], uv[1])

        if self.normals != None:
            normalwriter = GeomVertexWriter(vdata, 'normal')
            for norm in self.normals:
                normalwriter.addData3f((norm[0], norm[2], norm[1]))


        modes = {
            'triangle' : GeomTriangles(static_mode),
            'tristrip' : GeomTristrips(static_mode),
            'ngon' : GeomTrifans(static_mode),
            'line' : GeomLinestrips(static_mode),
            'point' : GeomPoints(static_mode),
            }

        if self.mode != 'line' or not self._triangles:
            prim = modes[self.mode]

            if self._triangles:
                if isinstance(self._triangles[0], int):
                    for t in self._triangles:
                        prim.addVertex(t)

                elif len(self._triangles[0]) >= 3: # if tris are tuples like this: ((0,1,2), (1,2,3))
                    for t in self._triangles:
                        if len(t) == 3:
                            for e in t:
                                prim.addVertex(e)
                        elif len(t) == 4: # turn quad into tris
                            prim.addVertex(t[0])
                            prim.addVertex(t[1])
                            prim.addVertex(t[2])
                            prim.addVertex(t[2])
                            prim.addVertex(t[3])
                            prim.addVertex(t[0])

            else:
                prim.addConsecutiveVertices(0, len(self.vertices))

            prim.close_primitive()
            geom = Geom(vdata)
            geom.addPrimitive(prim)

        else:   # line with segments defnined in triangles
            for line in self._triangles:
                prim = modes[self.mode]
                for e in line:
                    prim.addVertex(e)
                prim.close_primitive()
                geom = Geom(vdata)
                geom.addPrimitive(prim)


        self.geomNode = GeomNode('mesh')
        self.geomNode.addGeom(geom)
        self.attachNewNode(self.geomNode)

        if self.normals:
            self.normals = [tuple(e) for e in self.normals]
        self.recipe = f'Mesh({self.vertices}, {self._triangles}, {self.colors}, {self.uvs}, {self.normals}, {self.static}, "{self.mode}", {self.thickness})'
        # print('finished')

    @property
    def thickness(self):
        return self.getRenderModeThickness()

    @thickness.setter
    def thickness(self, value):
        self.setRenderModeThickness(value)

    @property
    def triangles(self):
        if self._triangles == None:
            self._triangles = [(i, i+1, i+2) for i in range(0, len(self.vertices), 3)]

        return self._triangles

    @triangles.setter
    def triangles(self, value):
        self._triangles = value


    def generate_normals(self, smooth=True):
        self.normals = list(generate_normals(self.vertices, self.triangles, smooth))
        self.generate()
        return self.normals


    def colorize(self, left=color.white, right=color.blue, down=color.red, up=color.green, back=color.white, forward=color.white, smooth=True):
        colorize(self, left, right, down, up, back, forward, smooth)


    def project_uvs(self, aspect_ratio):
        project_uvs(self, aspect_ratio)

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
    points = Entity(model=Mesh(vertices=verts, mode='point', thickness=6), color=color.red, z=-1.01)

    EditorCamera()
    app.run()
