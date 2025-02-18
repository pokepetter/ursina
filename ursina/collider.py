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
        if self.node_path is not None:
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


from panda3d.core import (CollisionNode, CollisionBox, CollisionSphere, CollisionCapsule,
                          CollisionPolygon, NodePath, GeomVertexReader)
from ursina.vec3 import Vec3
from ursina.mesh import Mesh

class MeshCollider(Collider):
    """
    Creates collision solids from a 3D mesh.
    
    Parameters:
        entity         : The entity to which the collider is attached.
        mesh           : The source mesh (either a ursina Mesh or a Panda3D NodePath). If None,
                         entity.model is used.
        center         : A tuple (x, y, z) offset applied to all vertices.
        auto_simplify  : If True, and if the mesh has more triangles than max_triangles,
                         a simplified collision shape (a bounding box) is created.
        max_triangles  : The threshold number of triangles above which simplification is used.
    """
    def __init__(self, entity, mesh=None, center=(0, 0, 0), auto_simplify=False, max_triangles=500):
        self.center = Vec3(center)
        if mesh is None and hasattr(entity, 'model'):
            mesh = entity.model
            # print('Auto generating mesh collider from entity\'s mesh')

        self.collision_polygons = []

        # Get a list of vertex positions (as Vec3) from the mesh
        vertices = []
        if isinstance(mesh, Mesh):
            vertices = self._extract_from_ursina_mesh(mesh)
        elif isinstance(mesh, NodePath):
            vertices = self._extract_from_nodepath(mesh)
        else:
            print('Error: MeshCollider does not support mesh of type:', type(mesh))
            return

        # If auto_simplify is enabled and the triangle count is too high,
        # create a simplified collision shape (bounding box)
        triangle_count = len(vertices) // 3
        if auto_simplify and triangle_count > max_triangles:
            bbox = self._compute_bounding_box(vertices)
            poly = CollisionBox(bbox['center'], bbox['x_size'], bbox['y_size'], bbox['z_size'])
            self.collision_polygons.append(poly)
        else:
            # Otherwise, create collision polygons (triangles)
            for idx in range(0, len(vertices) - 2, 3):
                # Create a triangle using three consecutive vertices;
                # note that we reverse the order to match Panda3D's expected winding.
                poly = CollisionPolygon(
                    vertices[idx + 2] + self.center,
                    vertices[idx + 1] + self.center,
                    vertices[idx]     + self.center
                )
                self.collision_polygons.append(poly)

        # Create a collision node and attach the generated solids.
        super().__init__(entity, self.collision_polygons)

    def _extract_from_ursina_mesh(self, mesh: Mesh):
        """Extracts vertex data from a ursina Mesh."""
        vertices = []
        if mesh.mode == 'triangle':
            # Assumes mesh.generated_vertices is a flat list of coordinates.
            for i in range(0, len(mesh.generated_vertices), 3):
                v = Vec3(*mesh.generated_vertices[i:i+3])
                vertices.append(v)
        elif mesh.mode == 'ngon':
            # Decompose the ngon into a fan of triangles.
            if len(mesh.vertices) < 3:
                return vertices
            first_v = Vec3(*mesh.vertices[0])
            for i in range(1, len(mesh.vertices) - 1):
                v2 = Vec3(*mesh.vertices[i])
                v3 = Vec3(*mesh.vertices[i+1])
                vertices.extend([first_v, v2, v3])
        else:
            print('Error: MeshCollider does not support mesh mode:', mesh.mode)
        return vertices

    def _extract_from_nodepath(self, nodepath: NodePath):
        """Extracts vertex data from a Panda3D NodePath by iterating over all GeomNodes."""
        vertices = []
        geom_node_paths = nodepath.findAllMatches('**/+GeomNode')
        for geom_np in geom_node_paths:
            geom_node = geom_np.node()
            for geom_index in range(geom_node.getNumGeoms()):
                geom = geom_node.getGeom(geom_index)
                vdata = geom.getVertexData()
                # Iterate over each primitive
                for prim_index in range(geom.getNumPrimitives()):
                    prim = geom.getPrimitive(prim_index).decompose()
                    vertex_reader = GeomVertexReader(vdata, 'vertex')
                    for prim_num in range(prim.getNumPrimitives()):
                        start = prim.getPrimitiveStart(prim_num)
                        end = prim.getPrimitiveEnd(prim_num)
                        # Assuming primitives decompose into triangles:
                        for vi in range(start, end):
                            vertex_index = prim.getVertex(vi)
                            vertex_reader.setRow(vertex_index)
                            vertex = vertex_reader.getData3()
                            vertices.append(Vec3(vertex))
        return vertices

    def _compute_bounding_box(self, vertices):
        """Computes the axis-aligned bounding box of a list of Vec3 vertices."""
        if not vertices:
            return {'center': Vec3(0, 0, 0), 'x_size': 0, 'y_size': 0, 'z_size': 0}
        xs = [v.x for v in vertices]
        ys = [v.y for v in vertices]
        zs = [v.z for v in vertices]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        center = Vec3((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2)
        return {
            'center': center + self.center,
            'x_size': (max_x - min_x) / 2,
            'y_size': (max_y - min_y) / 2,
            'z_size': (max_z - min_z) / 2
        }

    def remove(self):
        """Cleanly removes the collision solids."""
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
