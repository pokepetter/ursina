from ursina import *


class Sphere(Mesh):
    def __init__(self, radius=.5, subdivisions=0, mode='tristrip', **kwargs):
        X = .525731112119133606 * radius
        Z = .850650808352039932 * radius
        N = .0

        verts = (
            (-X, N, Z), (X, N, Z), (-X, N, -Z), (X, N, -Z),
            (N, Z, X), (N, Z, -X), (N, -Z, X), (N, -Z, -X),
            (Z, X, N), (-Z, X, N), (Z, -X, N), (-Z, -X, N)
        )

        verts = tuple([Vec3(x) for x in verts])

        faces = (
            (0, 4, 1), (0, 9, 4), (9, 5, 4), (4, 5, 8), (4, 8, 1),
            (8, 10, 1), (8, 3, 10), (5, 3, 8), (5, 2, 3), (2, 7, 3),
            (7, 10, 3), (7, 6, 10), (7, 11, 6), (11, 0, 6), (0, 1, 6),
            (6, 1, 10), (9, 0, 11), (9, 11, 2), (9, 2, 5), (7, 2, 11)
        )

        final_verts = []
        final_faces = []

        # Sub divide all of the faces
        for i in range(20):
            self.sub_divide(*(verts[j] for j in faces[i]), subdivisions, final_verts, final_faces)

        super().__init__(vertices=final_verts, triangles=final_faces, colors=None, mode=mode, **kwargs)

    @staticmethod
    def normalize_vert(v: Vec3):
        return v / sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

    def sub_divide(self, v_0, v_1, v_2, sub_divisions, vertices, faces):
        if sub_divisions <= 0:
            a = len(vertices)

            vertices.append(v_0)
            vertices.append(v_1)
            vertices.append(v_2)

            faces.append((a, a + 1, a + 2))
        else:
            v_01 = self.normalize_vert((v_0 + v_1) / 2.0)
            v_02 = self.normalize_vert((v_0 + v_2) / 2.0)
            v_12 = self.normalize_vert((v_1 + v_2) / 2.0)

            sub_divisions -= 1

            self.sub_divide(v_0, v_01, v_02, sub_divisions, vertices, faces)
            self.sub_divide(v_1, v_12, v_01, sub_divisions, vertices, faces)
            self.sub_divide(v_2, v_02, v_12, sub_divisions, vertices, faces)
            self.sub_divide(v_01, v_12, v_02, sub_divisions, vertices, faces)


if __name__ == '__main__':
    app = Ursina()
    Entity(model=Sphere(subdivisions=5), color=color.color(60, 1, 1, .5), x=0)
    Entity(model=Sphere(radius=0.15, subdivisions=6), color=color.color(1, 60, 1, .5), x=4)
    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    ed = EditorCamera(rotation_speed=200, panning_speed=200)
    app.run()
