from panda3d.core import CollisionNode, CollisionBox, CollisionSphere, CollisionPolygon
from panda3d.core import NodePath
from ursina.vec3 import Vec3
from ursina.mesh import Mesh


class Collider(NodePath):
    def __init__(self):
        super().__init__('box_collider')

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def remove(self):
        self.node_path.node().clearSolids()
        self.node_path.removeNode()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        if value:
            self.node_path.show()
        else:
            self.node_path.hide()
            pass


class BoxCollider(Collider):
    def __init__(self, entity, center=(0,0,0), size=(1,1,1)):
        super().__init__()
        size = [e/2 for e in size]
        size = [max(0.001, e) for e in size] # collider needs to have thickness
        self.shape = CollisionBox(Vec3(center[0], center[1], center[2]), size[0], size[1], size[2])
        # self.remove()
        self.collision_node = CollisionNode('CollisionNode')
        self.node_path = entity.attachNewNode(self.collision_node)
        self.node_path.node().addSolid(self.shape)
        self.visible = False
        # self.node_path.show()
        # for some reason self.node_path gets removed after this and can't be shown.

class SphereCollider(Collider):
    def __init__(self, entity, center=(0,0,0), radius=.5):
        super().__init__()
        self.shape = CollisionSphere(center[0], center[1], center[2], radius)
        self.node_path = entity.attachNewNode(CollisionNode('CollisionNode'))
        self.node_path.node().addSolid(self.shape)
        self.visible = False


class MeshCollider(Collider):
    def __init__(self, entity, mesh=None, center=(0,0,0)):
        super().__init__()
        center = Vec3(center)
        if mesh == None and entity.model:
            mesh = entity.model
            # print('''auto generating mesh collider from entity's mesh''')

        self.node_path = entity.attachNewNode(CollisionNode('CollisionNode'))
        self.collision_polygons = []

        if isinstance(mesh, Mesh):
            if mesh.triangles:
                triangles = mesh.triangles
                if not isinstance(mesh.triangles[0], tuple):
                    triangles = [triangles[i:i + 3] for i in range(0, len(triangles), 3)] # group into groups of three

                for tri in triangles:
                    if len(tri) == 3:
                        poly = CollisionPolygon(
                            Vec3(mesh.vertices[tri[2]]),
                            Vec3(mesh.vertices[tri[1]]),
                            Vec3(mesh.vertices[tri[0]]),
                            )
                        self.collision_polygons.append(poly)
                    elif len(tri) == 4:
                        poly = CollisionPolygon(
                            Vec3(mesh.vertices[tri[3]]),
                            Vec3(mesh.vertices[tri[2]]),
                            Vec3(mesh.vertices[tri[1]]),
                            Vec3(mesh.vertices[tri[0]]))
                        self.collision_polygons.append(poly)


            elif mesh.mode == 'triangle': # no triangle list, so take 3 and 3 vertices
                for i in range(0, len(mesh.vertices), 3):
                    poly = CollisionPolygon(
                        Vec3(mesh.vertices[i+2]),
                        Vec3(mesh.vertices[i+1]),
                        Vec3(mesh.vertices[i]),
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


        node = self.node_path.node()
        for poly in self.collision_polygons:
            node.addSolid(poly)
        self.visible = False


    def remove(self):
        self.node_path.node().clearSolids()
        self.collision_polygons.clear()
        self.node_path.removeNode()


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='sphere', x=2)
    e.collider = 'box'          # add BoxCollider based on entity's bounds.
    e.collider = 'sphere'       # add SphereCollider based on entity's bounds.
    e.collider = 'mesh'         # add MeshCollider matching the entity's model.
    e.collider = 'file_name'    # load a model and us it as MeshCollider.
    e.collider = e.model        # copy target model/Mesh and use it as MeshCollider.

    e.collider = BoxCollider(e, center=Vec3(0,0,0), size=Vec3(1,1,1))   # add BoxCollider at custom positions and size.
    e.collider = SphereCollider(e, center=Vec3(0,0,0), radius=.75)      # add SphereCollider at custom positions and size.
    e.collider = MeshCollider(e, mesh=e.model, center=Vec3(0,0,0))      # add MeshCollider with custom shape and center.

    m = Pipe(base_shape=Circle(6), thicknesses=(1, .5))
    e = Button(parent=scene, model='cube', collider='mesh', color=color.red, highlight_color=color.yellow)
    # e = Button(parent=scene, model='quad', collider=, color=color.lime, x=-1)

    EditorCamera()

    def input(key):
        if key == 'c':
            e.collider = None

    # def update():
    #     print(mouse.point)


    app.run()
