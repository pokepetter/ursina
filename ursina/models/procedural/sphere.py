from ursina import *


class Sphere(Mesh):
    def __init__(self, radius=.5, subdivisions=0, mode='tristrip', **kwargs):
        X=.525731112119133606 * radius
        Z=.850650808352039932 * radius
        N=0

        verts = (
            (-X,N,Z), (X,N,Z), (-X,N,-Z), (X,N,-Z),
            (N,Z,X), (N,Z,-X), (N,-Z,X), (N,-Z,-X),
            (Z,X,N), (-Z,X, N), (Z,-X,N), (-Z,-X, N)
        )

        faces = (
            0,4,1,0,9,4,9,5,4,4,5,8,4,8,1,
            8,10,1,8,3,10,5,3,8,5,2,3,2,7,3,
            7,10,3,7,6,10,7,11,6,11,0,6,0,1,6,
            6,1,10,9,0,11,9,11,2,9,2,5,7,2,11
        )
        colors = None

        super().__init__(vertices=verts, triangles=faces, colors=colors, mode=mode, **kwargs)


if __name__ == '__main__':
    app = Ursina()
    Entity(model=Sphere(), color=color.color(60,1,1,.3), x=4)
    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    app.run()
