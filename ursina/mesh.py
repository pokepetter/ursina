from panda3d.core import NodePath
from panda3d.core import GeomVertexData, GeomVertexFormat, Geom, GeomVertexWriter, GeomNode
from panda3d.core import GeomTriangles, GeomTristrips, GeomTrifans
from panda3d.core import GeomLinestrips, GeomPoints
from panda3d.core import TexGenAttrib, TextureStage
from panda3d.core import LVector4f
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
        # overridden __eq__ to allow for both str and InputEvent comparisons
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

    def __init__(self, vertices=None, triangles=None, colors=None, uvs=None, normals=None, static=True, mode='triangle', thickness=1, render_points_in_3d=True):
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

        for var in (('vertices', vertices), ('triangles', triangles), ('colors', colors), ('uvs', uvs), ('normals', normals)):
            name, value = var
            if value is None:
                setattr(self, name, [])

        if self.vertices != []:
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
                colorwriter.addData4f(LVector4f(*c))

        if self.uvs:
            uvwriter = GeomVertexWriter(vdata, 'texcoord')
            for uv in self.uvs:
                uvwriter.addData2f(uv[0], uv[1])

        if self.normals is not None:
            normalwriter = GeomVertexWriter(vdata, 'normal')
            for norm in self.normals:
                normalwriter.addData3f(*norm)


        if self.mode != 'line' or not self._triangles:
            self.indices = []

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

            if not self.indices:
                return

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
        if self._triangles is None:
            self._triangles = [(i, i+1, i+2) for i in range(0, len(self.vertices), 3)]

        return self._triangles

    @triangles.setter
    def triangles(self, value):
        self._triangles = value


    def generate_normals(self, smooth=True):
        self.normals = list(generate_normals(self.vertices, self.triangles, smooth))
        self.generate()
        return self.normals


    def colorize(self, left=color.white, right=color.blue, down=color.red, up=color.green, back=color.white, forward=color.white, smooth=True, world_space=True, strength=1):
        colorize(self, left, right, down, up, back, forward, smooth, world_space, strength)


    def project_uvs(self, aspect_ratio=1, direction='forward'):
        project_uvs(self, aspect_ratio)


    def clear(self, regenerate=True):
        self.vertices, self.triangles, self.colors, self.uvs, self.normals = [], [], [], [], []
        if regenerate:
            self.generate()


    def save(self, name='', folder:Path=application.compressed_models_folder, flip_faces=False):
        if not application.compressed_models_folder.exists():
            application.compressed_models_folder.mkdir()

        if not name and hasattr(self, 'path'):
            name = self.path.stem
            if '.' not in name:
                name += '.ursinamesh'

        if name.endswith('ursinamesh'):
            with open(folder / name, 'w') as f:
                # recipe = self.recipe.replace('LVector3f', '')
                f.write(self.recipe)
            print('saved .ursinamesh to:', folder / name)

        elif name.endswith('.obj'):
            from ursina.mesh_exporter import ursinamesh_to_obj
            import os
            # Remove the file extension, so we don't get 'name.obj.obj'
            name = str(os.path.splitext(name)[0])
            ursinamesh_to_obj(self, name, folder, flip_faces)

        elif name.endswith('.dae'):
            from ursina.mesh_exporter import ursinamesh_to_dae
            import os
            # Remove the file extension, so we don't get 'name.dae.dae'
            name = str(os.path.splitext(name)[0])
            ursinamesh_to_dae(self, name, folder)

        elif name.endswith('.bam'):
            success = self.writeBamFile(folder / name)
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

    window.color = color.black
    EditorCamera()

    app.run()
