from panda3d.core import MeshDrawer, NodePath
from panda3d.core import GeomVertexData, GeomVertexFormat, Geom, GeomVertexWriter, GeomNode
from panda3d.core import GeomTriangles, GeomTristrips, GeomTrifans
from panda3d.core import GeomLines, GeomLinestrips, GeomPoints

class Mesh(NodePath):

    def __init__(self, vertices=None, triangles=None, colors=None, uvs=None, normals=None, static=True, mode='ngon', thickness=1):
        super().__init__('mesh')

        self.vertices = vertices
        self.triangles = triangles
        self.colors = colors
        self.uvs = uvs
        self.normals = normals
        self.static = static
        self.mode = mode
        self.thickness = thickness

        if self.vertices:
            self.generate()


    def generate(self):
        if not self.vertices:
            return

        if hasattr(self, 'geomNode'):
            self.geomNode.removeNode()

        static_mode = Geom.UHStatic if self.static else Geom.UHDynamic

        formats = {
            (0,0,0) : GeomVertexFormat.getV3(),
            (1,0,0) : GeomVertexFormat.getV3c4(),
            (0,1,0) : GeomVertexFormat.getV3t2(),
            (1,0,1) : GeomVertexFormat.getV3n3c4(),
            (1,1,0) : GeomVertexFormat.getV3c4t2(),
            (0,1,1) : GeomVertexFormat.getV3n3t2(),
            (1,1,1) : GeomVertexFormat.getV3n3c4t2()
            }

        vertex_format = formats[(self.colors != None, self.uvs != None, self.normals != None)]
        vdata = GeomVertexData('name', vertex_format, static_mode)
        vdata.setNumRows(len(self.vertices)) # for speed

        # normal = GeomVertexWriter(vdata, 'normal')
        # texcoord = GeomVertexWriter(vdata, 'texcoord')

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
        # normal.addData3f(0, 0, 1)
        # texcoord.addData2f(1, 0)
        modes = {
            'triangle' : GeomTriangles(static_mode),
            'tristrip' : GeomTristrips(static_mode),
            'ngon' : GeomTrifans(static_mode),
            'line' : GeomLines(static_mode),
            'lines' : GeomLinestrips(static_mode),
            'point' : GeomPoints(static_mode),
            }
        if self.mode == 'line' and len(self.vertices) % 2 > 0:
            if len(self.vertices) == 1:
                self.mode = point
            print('warning: number of vertices must be even for line mode, ignoring last vert')
            self.vertices = self.vertices[ : len(self.vertices)-1]

        prim = modes[self.mode]

        if self.triangles:
            for t in self.triangles:
                prim.addVertex(t)
        else:
            prim.addConsecutiveVertices(0, len(self.vertices))

        prim.close_primitive()

        geom = Geom(vdata)
        geom.addPrimitive(prim)

        self.geomNode = GeomNode('mesh')
        self.geomNode.addGeom(geom)
        self.attachNewNode(self.geomNode)
        # print('finished')

        self.recipe = '''
            Mesh(vertices={}, \ntriangles={}, \ncolors={}, \nuvs={}, \nnormals={}, \nstatic={}, \nmode='{}', \nthickness={})
            '''.format(
                str(tuple([(e[0],e[1],e[2]) for e in self.vertices])), str(self.triangles), str(self.colors), str(self.uvs),
                str(self.normals), str(self.static), str(self.mode), str(self.thickness)).strip()

    @property
    def thickness(self):
        return self.getRenderModeThickness()

    @thickness.setter
    def thickness(self, value):
        self.setRenderModeThickness(value)

    @property
    def world_vertices(self):
        print('wwwwwwwwwwwwwwwwwww', self.vertices[0])




if __name__  == '__main__':
    from ursina import *
    app = Ursina()
    verts = ((0,0,0), (1,0,0), (.5, 1, 0), (-.5,1,0))
    # tris = (1, 2, 0, 2, 3, 0)
    tris = (0,1,2, 0,2,3)
    uvs = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
    # colors = (color.red, color.blue, color.lime, color.black)
    colors = ()
    # m = Mesh(vertices=verts, triangles=tris, uvs=uvs, colors=colors)
    m = Mesh()
    m.vertices = verts
    m.triangles = tris
    m.uvs = uvs
    m.generate()
    e = Entity()
    e.model = m
    e.texture = 'white_cube'
    # e.show_vertices()
    EditorCamera()
    app.run()
