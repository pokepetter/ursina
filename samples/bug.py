from ursina import *

app = Ursina()


from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import array
import struct


#
# # define the vertex positions as a sequence of x, y, z coordinates;
# coords = [1., -3., 7., -4., 12., 5., 8., 2., -1., -6., 14., -11.]
# # either convert this sequence to an array of bytes...
# # (note that if you call tobytes() on it, you don't need to call
# # cast("f") on the memoryview, below)
# pos_data = array.array("f", coords)#.tobytes()
# # ...or, alternatively, use a struct:
# #        pos_data = struct.pack("{:d}f".format(len(coords)), *coords)
#
# vertex_format = GeomVertexFormat.get_v3()
# vertex_data = GeomVertexData("vertex_data", vertex_format, Geom.UH_static)
# # make sure the vertex vertices has the correct size by setting the exact
# # number of rows *before* using a memoryview, since you cannot change
# # its size while working with that memoryview; call unclean_set_num_rows
# # if there isn't any vertices in the vertex table yet, as in this example
# vertex_data.unclean_set_num_rows(4)
# pos_array = vertex_data.modify_array(0)
# # create a memoryview from the GeomVertexArrayData
# # (note that you should not call cast("f") on it if you used a struct
# # for the position vertices)
# memview = memoryview(pos_array).cast("B").cast("f")
# # assign the vertex position vertices to a slice of the memoryview
# # (in this case the entire memoryview)
# memview[:] = pos_data
# print("Array:\n", vertex_data.get_array(0))

tri_data = array.array("H", [0, 1, 2, 0, 2, 3])
tris_prim = GeomTriangles(Geom.UH_static)
tris_prim.reserve_num_vertices(len(tri_data))
tris_array = tris_prim.modify_vertices()

tris_array.unclean_set_num_rows(len(tri_data));
memview = memoryview(tris_array)
print('Memview content : {}'.format(memview.tolist()))
print('Memview format : {}'.format(memview.format))
print('Memview length : {}'.format(len(memview)))
memview[:] = tri_data
print('Copy to memview : {}'.format(memview.tolist()))
print('tri_data :')
print(tris_prim)





from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
import array


def create_cylinder(parent, radius, height, segments):

    segs_c = segments["circular"]
    segs_h = segments["height"]
    delta_angle = 2 * pi / segs_c
    vertices = array.array("f", [])
    tri_data = array.array("I", [])

    for i in range(segs_h + 1):

        z = height * i / segs_h

        for j in range(segs_c):
            angle = delta_angle * j
            x = radius * cos(angle)
            y = radius * sin(angle)
            vertices.extend((x, y, z))
            vertices.extend(Vec3(x, y, 0.).normalized())

    for i in range(segs_h):

        for j in range(segs_c - 1):
            vi1 = (i + 1) * segs_c + j
            vi2 = vi1 - segs_c
            vi3 = vi2 + 1
            vi4 = vi1 + 1
            tri_data.extend((vi1, vi2, vi3))
            tri_data.extend((vi1, vi3, vi4))

        vi1 = i * segs_c
        vi2 = vi1 + segs_c
        vi3 = vi2 + segs_c - 1
        vi4 = vi1 + segs_c - 1
        tri_data.extend((vi1, vi2, vi3))
        tri_data.extend((vi1, vi3, vi4))

    vert_count = segs_c * (segs_h + 1)
    vertex_format = GeomVertexFormat.get_v3n3()
    vertex_data = GeomVertexData("vertex_data", vertex_format, Geom.UH_static)
    vertex_data.unclean_set_num_rows(vert_count)
    data_array = vertex_data.modify_array(0)
    memview = memoryview(data_array).cast("B").cast("f")
    memview[:] = vertices

    tris_prim = GeomTriangles(Geom.UH_static)
    tris_prim.set_index_type(Geom.NT_uint32)
    tris_prim.reserve_num_vertices(len(tri_data))
    tris_array = tris_prim.modify_vertices()
    tris_array.unclean_set_num_rows(len(tri_data))
    memview = memoryview(tris_array).cast("B").cast("I")
    memview[:] = tri_data

    geom = Geom(vertex_data)
    geom.add_primitive(tris_prim)
    node = GeomNode("cylinder_node")
    node.add_geom(geom)
    cylinder = parent.attach_new_node(node)

    return cylinder


class MyApp(ShowBase):

    def __init__(self):

        ShowBase.__init__(self)

        # set up a light source
        p_light = PointLight("point_light")
        p_light.set_color((1., 1., 1., 1.))
        self.light = self.camera.attach_new_node(p_light)
        self.light.set_pos(5., -10., 7.)
        self.render.set_light(self.light)

        radius = 2.
        height = 5.
        segments = {"circular": 5, "height": 3}
        # create a cylinder parented to the scene root
        self.cylinder = create_cylinder(self.render, radius, height, segments)
        # create a matrix describing the inverse of the pivot position
        # (the "object-origin-to-pivot" transformation; in this example,
        # the pivot is located at the center of the cylinder)...
        mat = Mat4.translate_mat(0., 0., -height * .5)
        # ...combine it with a matrix describing a rotation about that
        # pivot point...
        mat *= Mat4.rotate_mat(30., Vec3(1., -1., 0.))
        # ...and finally combine this with another matrix, this time
        # describing the pivot position itself
        # (the "pivot-to-object-origin" transformation)
        mat *= Mat4.translate_mat(0., 0., height * .5)
        vert_count = segments["circular"] * (segments["height"] + 1)
        vert_count_half = vert_count // 2
        rows = SparseArray()
        # set the bits corresponding to the row indices of the vertices to be
        # transformed to "on" (in this example the vertices in the top half
        # of the cylinder)
        rows.set_range(vert_count - vert_count_half, vert_count_half)
        vertex_data = self.cylinder.node().modify_geom(0).modify_vertex_data()
        vertex_data.transform_vertices(mat, rows)




app.run()
