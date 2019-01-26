from panda3d.core import MeshDrawer, NodePath
from panda3d.core import GeomVertexData, GeomVertexFormat, Geom, GeomVertexWriter, GeomNode
from panda3d.core import GeomTriangles, GeomTristrips, GeomTrifans
from panda3d.core import GeomLines, GeomLinestrips, GeomPoints
from ursina.internal_scripts.generate_normals import generate_normals


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

        self.recipe = 'Mesh()'
        if self.vertices:
            self.generate()


    def generate(self):
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
        vertex_format = formats[(self.colors != None, self.uvs != None, self.normals != None)]
        vdata = GeomVertexData('name', vertex_format, static_mode)
        vdata.setNumRows(len(self.vertices)) # for speed

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

        if self.normals != None:
            normalwriter = GeomVertexWriter(vdata, 'normal')
            for norm in self.normals:
                normalwriter.addData3f((v[0], v[2], v[1]))
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

        self.geomNode = GeomNode('mesh')
        self.geomNode.addGeom(geom)
        self.attachNewNode(self.geomNode)
        # print('finished')

        self.recipe = f'''Mesh(
            vertices={str(tuple([(e[0],e[1],e[2]) for e in self.vertices]))},
            triangles={self._triangles},
            colors={self.colors},
            uvs={self.uvs},
            normals={self.normals},
            static={self.static},
            mode='{self.mode}',
            thickness={self.thickness}
            )'''

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


    def generate_normals(self):
        self.normals = list(generate_normals(self.vertices, self.triangles))




if __name__  == '__main__':
    from ursina import *
    app = Ursina()
    # verts = ((0,0,0), (1,0,0), (.5, 1, 0), (-.5,1,0))
    # tris = (1, 2, 0, 2, 3, 0)
    # tris = ((0,1,2), (0,2,3))
    # # tris = ((0,1,2,3),)
    # uvs = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
    # colors = (color.red, color.blue, color.lime, color.black)
    sphere = Sphere()
    # print(sphere.vertices, sphere.triangles)
    verts, tris = sphere.vertices, sphere.triangles
    # m = Mesh(vertices=verts, triangles=tris, uvs=uvs, colors=colors)
    m = Mesh()
    m.mode = 'triangle'
    m.vertices = verts
    m.triangles = tris
    # m.normals = ((0,1,0), ) * len(verts)
    def surface_normal(poly):
        n = [0.0, 0.0, 0.0]

        for i, v_curr in enumerate(poly):
            v_next = poly[(i+1) % len(poly)]
            n[0] += (v_curr[1] - v_next[1]) * (v_curr[2] + v_next[2])
            n[1] += (v_curr[2] - v_next[2]) * (v_curr[0] + v_next[0])
            n[2] += (v_curr[0] - v_next[0]) * (v_curr[1] + v_next[1])

        normalised = [i/sum(n) for i in n]

        return normalised

        # n[0] += (v_curr.y - v_next.y) * (v_curr.z + v_next.z)

    # poly = (verts[tris[0][0]], verts[tris[0][1]], verts[tris[0][2]])
    # print('.......', surface_normal(poly))
    all_verts = list()
    if isinstance(tris[0], int):
        for t in tris:
            all_verts.append(verts[t])
    else:
        for tup in tris:
            length = len(tup)
            if length == 3:
                all_verts.append(verts[tup[0]])
                all_verts.append(verts[tup[1]])
                all_verts.append(verts[tup[2]])
            elif length == 4:
                all_verts.append(verts[tup[0]])
                all_verts.append(verts[tup[1]])
                all_verts.append(verts[tup[2]])
                all_verts.append(verts[tup[2]])
                all_verts.append(verts[tup[3]])
                all_verts.append(verts[tup[0]])

    # print(len(verts), len(all_verts))
    norms = list()
    for i in range(0, len(all_verts), 3):
        # print((all_verts[i], all_verts[i+1], all_verts[i+2]))
        face_normal = surface_normal((all_verts[i], all_verts[i+1], all_verts[i+2]))
        norms.append(face_normal)
        norms.append(face_normal)
        norms.append(face_normal)

    # m.uvs = uvs
    m.normals = norms

    # m.colors = [color.rgb(abs(n[0]), abs(n[1]), abs(n[2])) for n in norms]
    # print(m.normals)
    # m.colors = [color.random_color() for i in range(len(tris))]
    cols = list()
    for i in range(0, len(verts), 3):
        # col = color.random_color()
        col = color.colors[color.color_names[i]]
        cols.append(col)
        cols.append(col)
        cols.append(col)

    # colors = list()
    # for i in range(0, len(verts), 3):


    # print(colors)
    m.colors = cols
    m.generate()
    # m.generate()
    # e.model = m
    e = Entity(model=m)
    # e.texture = 'white_cube'
    # e.show_vertices()
    # e.set_shader ('D:/Dropbox/programming/software/ursina/ursina/internal_shaders/normals.sha')

    # from panda3d.core import DirectionalLight
    # light = render.attachNewNode(DirectionalLight('light'))
    # render.setLight(light)
    # print(e.shader)

    EditorCamera()
    app.run()
