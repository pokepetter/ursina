from ursina import Mesh, Vec3, rotate_point_2d


class Cone(Mesh):
    def __init__(self, resolution=4, radius=.5, height=1, add_bottom=True, mode='triangle', **kwargs):

        v = Vec3(radius, 0, 0)
        origin = Vec3(0,0,0)
        degrees_to_rotate = 360 / resolution

        verts = []
        for i in range(resolution):
            verts.append(Vec3(v[0], 0, v[1]))
            v = rotate_point_2d(v, origin, -degrees_to_rotate)
            verts.append(Vec3(v[0], 0, v[1]))

            verts.append(Vec3(0,height,0))
        if add_bottom:
            for i in range(resolution):
                verts.append(Vec3(v[0], 0, v[1]))
                verts.append(Vec3(0,0,0))
                v = rotate_point_2d(v, origin, -degrees_to_rotate)
                verts.append(Vec3(v[0], 0, v[1]))


        super().__init__(vertices=verts, uvs=[e.xy for e in verts], mode=mode, **kwargs)


if __name__ == '__main__':
    from ursina import Ursina, Entity, color, EditorCamera
    app = Ursina()
    e = Entity(model=Cone(3), texture='brick')

    # # rotate model
    # for i, v in enumerate(e.model.vertices):
    #     x, y = rotate_point_2d((v.x, v.y), (0,0), 90)
    #
    #     e.model.vertices[i] = Vec3(x, y, v.z)
    #
    # e.model.generate()

    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    ed = EditorCamera()
    app.run()
