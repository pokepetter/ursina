from math import sqrt


def distance(a, b):
    return sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2 + (b[2] - a[2])**2)


def merge_overlapping_vertices(vertices, triangles=None, max_distance=.1):

    if triangles == None:
        triangles = [(i, i+1, i+2) for i in range(0, len(vertices), 3)]

    if triangles[0] is int:
        triangles = [(triangles[i], triangles[i+1], triangles[i+2]) for i in range(0, len(triangles), 3)]

    unique = list()
    triangles = list(triangles)

    for i, v in enumerate(vertices):
        for j, u in enumerate(unique):
            if distance(v, u) <= max_distance:
                # print('found overlapping vertices!', i, 'could be', j)
                for k, t in enumerate(triangles):
                    if t == i:
                        triangles[k] = j
                        # for v in verts

        unique.append(v)

    return unique, triangles


if __name__ == '__main__':
    verts = ((0,0,0), (1,0,0), (1,1,0), (0,0,0), (1,1,0), (0,1,0))
    tris = (0,1,2,3,4,5)

    new_verts, new_tris = merge_overlapping_vertices(verts, tris)
    print('verts:', (verts), (new_verts))
    print('tris:', (tris), (new_tris))

    from ursina import *
    app = Ursina()

    e = Entity(model=Mesh(new_verts, new_tris, mode='triangle'))
    EditorCamera()

    app.run()
    # m = Cylinder(8)
    # calculate_normals(m.vertices)
