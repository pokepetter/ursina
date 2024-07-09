from panda3d.core import CollisionNode, CollisionBox, CollisionSphere, CollisionCapsule, CollisionPolygon
from panda3d.core import NodePath
from ursina.vec3 import Vec3
from ursina.mesh import Mesh


class Collider(NodePath):
    def __init__(self, entity, shape):
        super().__init__('collider')
        self.collision_node = CollisionNode('CollisionNode')

        self.shape = shape
        self.node_path = entity.attachNewNode(self.collision_node)

        if isinstance(shape, (list, tuple)):
            for e in shape:
                self.node_path.node().addSolid(e)
        else:
            self.node_path.node().addSolid(self.shape)


    def remove(self):
        self.node_path.node().clearSolids()
        self.node_path.removeNode()
        self.node_path = None
        # print('remove  collider')


    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        if value:
            self.node_path.show()
        else:
            self.node_path.hide()


class BoxCollider(Collider):
    def __init__(self, entity, center=(0,0,0), size=(1,1,1)):
        self.center = center
        self.size = size

        size = [e/2 for e in size]
        size = [max(0.001, e) for e in size] # collider needs to have thickness
        super().__init__(entity, CollisionBox(Vec3(center[0], center[1], center[2]), size[0], size[1], size[2]))


class SphereCollider(Collider):
    def __init__(self, entity, center=(0,0,0), radius=.5):
        self.center = center
        self.radius = radius
        super().__init__(entity, CollisionSphere(center[0], center[1], center[2], radius))


class CapsuleCollider(Collider):
    def __init__(self, entity, center=(0,0,0), height=2, radius=.5):
        self.center = center
        self.height = height
        self.radius = radius
        super().__init__(entity, CollisionCapsule(center[0], center[1] + radius, center[2], center[0], center[1] + height, center[2], radius))


class MeshCollider(Collider):
    def __init__(self, entity, mesh=None, center=(0,0,0)):
        self.center = center
        center = Vec3(center)
        if mesh is None and entity.model:
            mesh = entity.model
            # print('''auto generating mesh collider from entity's mesh''')

        self.collision_polygons = []

        if isinstance(mesh, Mesh):
            if mesh.mode == 'triangle':
                for i in range(0, len(mesh.generated_vertices), 3):
                    poly = CollisionPolygon(
                        Vec3(*mesh.generated_vertices[i+2]),
                        Vec3(*mesh.generated_vertices[i+1]),
                        Vec3(*mesh.generated_vertices[i]),
                        )
                    self.collision_polygons.append(poly)

            elif mesh.mode == 'ngon':
                # NOTE: does not support vertices len < 3. Is already being intercepted by pandas3D.
                for i in range(2, len(mesh.vertices)):
                    poly = CollisionPolygon(
                        Vec3(*mesh.vertices[i]),
                        Vec3(*mesh.vertices[i - 1]),
                        Vec3(*mesh.vertices[0]),
                    )
                    self.collision_polygons.append(poly)
            else:
                print('error: mesh collider does not support', mesh.mode, 'mode')
                return None


        elif isinstance(mesh, NodePath):
            from panda3d.core import GeomVertexReader
            verts = []
            geomNodeCollection = mesh.findAllMatches('**/+GeomNode')
            for nodePath in geomNodeCollection:
                geomNode = nodePath.node()
                for i in range(geomNode.getNumGeoms()):
                    geom = geomNode.getGeom(i)
                    vdata = geom.getVertexData()
                    for i in range(geom.getNumPrimitives()):
                        prim = geom.getPrimitive(i)
                        vertex_reader = GeomVertexReader(vdata, 'vertex')
                        prim = prim.decompose()

                        for p in range(prim.getNumPrimitives()):
                            s = prim.getPrimitiveStart(p)
                            e = prim.getPrimitiveEnd(p)
                            for i in range(s, e):
                                vi = prim.getVertex(i)
                                vertex_reader.setRow(vi)
                                verts.append(vertex_reader.getData3())

            for i in range(0, len(verts)-3, 3):
                p = CollisionPolygon(Vec3(verts[i+2]), Vec3(verts[i+1]), Vec3(verts[i]))
                self.collision_polygons.append(p)

        super().__init__(entity, self.collision_polygons)


    def remove(self):
        self.node_path.node().clearSolids()
        self.collision_polygons.clear()
        self.node_path.removeNode()



if __name__ == '__main__':
    from ursina import *
    from ursina import Ursina, Entity, Pipe, Circle, Button, scene, EditorCamera, color
    app = Ursina()

    e = Button(parent=scene, model='sphere', x=2)
    e.collider = 'box'          # add BoxCollider based on entity's bounds.
    e.collider = 'sphere'       # add SphereCollider based on entity's bounds.
    e.collider = 'capsule'      # add CapsuleCollider based on entity's bounds.
    e.collider = 'mesh'         # add MeshCollider matching the entity's model.
    e.collider = 'file_name'    # load a model and us it as MeshCollider.
    e.collider = e.model        # copy target model/Mesh and use it as MeshCollider.

    e.collider = BoxCollider(e, center=Vec3(0,0,0), size=Vec3(1,1,1))   # add BoxCollider at custom positions and size.
    e.collider = SphereCollider(e, center=Vec3(0,0,0), radius=.75)      # add SphereCollider at custom positions and size.
    e.collider = CapsuleCollider(e, center=Vec3(0,0,0), height=3, radius=.75) # add CapsuleCollider at custom positions and size.
    e.collider = MeshCollider(e, mesh=e.model, center=Vec3(0,0,0))      # add MeshCollider with custom shape and center.

    m = Pipe(base_shape=Circle(6), thicknesses=(1, .5))
    e = Button(parent=scene, model='cube', collider='mesh', color=color.red, highlight_color=color.yellow)
    # e = Button(parent=scene, model='quad', collider=, color=color.lime, x=-1)

    sphere = Button(parent=scene, model='icosphere', collider='mesh', color=color.red, highlight_color=color.yellow, x=4)

    EditorCamera()

    def input(key):
        if key == 'c':
            e.collider = None

    # def update():
    #     print(mouse.point)


    app.run()
