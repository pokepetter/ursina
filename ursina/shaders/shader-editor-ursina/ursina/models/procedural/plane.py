from ursina import *


class Plane(Mesh):
    def __init__(self, subdivisions=(1,1), mode='triangle', **kwargs):

        self.vertices, self.triangles = list(), list()
        self.uvs = list()

        w, h = subdivisions
        i = 0

        for z in range(h+1):
            for x in range(w+1):
                self.vertices.append(Vec3((x/w)-.5, 0, (z/h)-.5))
                self.uvs.append((x/w, z/h))

                if x > 0 and z > 0:
                    self.triangles.append((i, i-1, i-w-2, i-w-1))

                i += 1

        super().__init__(vertices=self.vertices, triangles=self.triangles, uvs=self.uvs, mode=mode, **kwargs)



if __name__ == '__main__':
    app = Ursina()

    front =  Entity(model=Plane(subdivisions=(3,6)), texture='brick', rotation_x=-90)

    _ed = EditorCamera()
    Entity(model='cube', color=color.green, scale=.05)
    app.run()
