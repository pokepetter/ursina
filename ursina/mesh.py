from panda3d.core import MeshDrawer, NodePath
from panda3d.core import GeomVertexData, GeomVertexFormat, Geom, GeomVertexWriter, GeomNode
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
        # overriden __eq__ to allow for both str and InputEvent comparisons
        if isinstance(other, MeshModes):
            return self.value == other.value
        return self.value == other




class Mesh(NodePath):

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
        'ngon' : GeomTrifans,
        'line' : GeomLinestrips,
        'point' : GeomPoints,
        }

    def __init__(self, vertices=None, triangles=None, colors=None, uvs=None, normals=None, static=True, mode='triangle', thickness=1):
        super().__init__('mesh')

        self.vertices = vertices
        self.triangles = triangles
        self.colors = colors
        self.uvs = uvs
        self.normals = normals
        self.static = static
        self.mode = mode
        self.thickness = thickness

        for var in (('vertices', vertices), ('triangles', triangles), ('colors', colors), ('uvs', uvs), ('normals', normals)):
            name, value = var
            if value is None:
                setattr(self, name, list())

        if self.vertices:
            self.generate()


    def generate(self):  # call this after setting some of the variables to update it
        if hasattr(self, 'geomNode'):
            self.geomNode.removeAllGeoms()

        static_mode = Geom.UHStatic if self.static else Geom.UHDynamic
        vertex_format = Mesh._formats[(bool(self.colors), bool(self.uvs), bool(self.normals))]
        vdata = GeomVertexData('name', vertex_format, static_mode)
        vdata.setNumRows(len(self.vertices)) # for speed
        if not hasattr(self, 'geomNode'):
            self.geomNode = GeomNode('mesh')
            self.attachNewNode(self.geomNode)

        vertexwriter = GeomVertexWriter(vdata, 'vertex')
        for v in self.vertices:
            vertexwriter.addData3f(*v)

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
                normalwriter.addData3f(*norm)


        if self.mode != 'line' or not self._triangles:
            self.indices = list()

            if self._triangles:
                if isinstance(self._triangles[0], int):
                    for t in self._triangles:
                        self.indices.append(t)

                elif len(self._triangles[0]) >= 3: # if tris are tuples like this: ((0,1,2), (1,2,3))
                    for t in self._triangles:
                        if len(t) == 3:
                            self.indices.extend(t)

                        elif len(t) == 4: # turn quad into tris
                            self.indices.extend([t[i]for i in (0,1,2,2,3,0)])

            else:
                self.indices = [i for i in range(len(self.vertices))]

            prim = Mesh._modes[self.mode](static_mode)

            self.generated_vertices = [self.vertices[i] for i in self.indices]
            for v in self.indices:
                prim.addVertex(v)

            prim.close_primitive()
            geom = Geom(vdata)
            geom.addPrimitive(prim)
            self.geomNode.addGeom(geom)

        else:   # line with segments defined in triangles
            for line in self._triangles:
                prim = Mesh._modes[self.mode](static_mode)
                for e in line:
                    prim.addVertex(e)
                prim.close_primitive()
                geom = Geom(vdata)
                geom.addPrimitive(prim)
                self.geomNode.addGeom(geom)

        if self.mode == 'point':
            self.setTexGen(TextureStage.getDefault(), TexGenAttrib.MPointSprite)
            # self.set_render_mode_perspective(True)


        # print('finished')

    @property
    def recipe(self):
        if hasattr(self, '_recipe'):
            return self._recipe

        return dedent(f'''
            Mesh(
                vertices={[tuple(e) for e in self.vertices]},
                triangles={self._triangles},
                colors={[tuple(e) for e in self.colors]},
                uvs={self.uvs},
                normals={[tuple(e) for e in self.normals]},
                static={self.static},
                mode="{self.mode}",
                thickness={self.thickness}
            )
        ''')
    @recipe.setter
    def recipe(self, value):
        self._recipe = value


    def __add__(self, other):
        self.vertices += other.vertices
        self.triangles += other.triangles
        if other.colors:
            self.colors += other.colors
        else:
            self.colors += (color.white, ) * len(other.vertices)

        self.normals += other.normals
        self.uvs += other.uvs


    def __deepcopy__(self, memo):
        m = Mesh(self.vertices, self.triangles, self.colors, self.uvs, self.normals, self.static, self.mode, self.thickness)
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


    def colorize(self, left=color.white, right=color.blue, down=color.red, up=color.green, back=color.white, forward=color.white, smooth=True, world_space=True):
        colorize(self, left, right, down, up, back, forward, smooth, world_space)


    def project_uvs(self, aspect_ratio=1, direction='forward'):
        project_uvs(self, aspect_ratio)


    def clear(self, regenerate=True):
        self.vertices, self.triangles, self.colors, self.uvs, self.normals = list(), list(), list(), list(), list()
        if regenerate:
            self.generate()


    def save(self, name='', path=application.compressed_models_folder):
        if not application.compressed_models_folder.exists():
            application.compressed_models_folder.mkdir()

        if not name and hasattr(self, 'path'):
            name = self.path.stem
            if not '.' in name:
                name += '.ursinamesh'

        if name.endswith('ursinamesh'):
            with open(path / name, 'w') as f:
                # recipe = self.recipe.replace('LVector3f', '')
                f.write(self.recipe)
            print('saved .ursinamesh to:', path / name)

        elif name.endswith('.obj'):
            from ursina.mesh_importer import ursina_mesh_to_obj
            ursina_mesh_to_obj(self, name, path)

        elif name.endswith('.bam'):
            success = self.writeBamFile(path / name)
            print('saved .bam to:', path / name)




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

    EditorCamera()
    app.run()
