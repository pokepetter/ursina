from ursina import *


class Plane(Mesh):
    def __init__(self, subdivisions=(1,1), mode='triangle', **kwargs):

        self.vertices, self.triangles = list(), list()
        i = 0

        w, h = subdivisions

        for y in range(h):
            for x in range(w):
                self.vertices.extend((
                    ((x/w) -.5,       0, (y/h) -.5),
                    (((x+1)/w) -.5,   0, (y/h) -.5),
                    (((x+1)/w) -.5,   0, ((y+1)/h) -.5),
                    ((x/w) -.5,       0, ((y+1)/h) -.5)
                ))

                self.triangles.append([e+i for e in (0,1,2,3)])
                i += 4


        super().__init__(vertices=self.vertices, triangles=self.triangles, mode=mode, **kwargs)




if __name__ == '__main__':
    app = Ursina()

    front =  Entity(model=Plane(subdivisions=(3,6)), z=-.5, rotation_x=-90)

    _ed = EditorCamera()
    app.run()
