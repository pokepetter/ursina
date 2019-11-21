from ursina import *
from ursina.models.procedural.plane import Plane


def Cube(bevel=0, subdivisions=(1,1,1), mode='triangle', **kwargs):

    if subdivisions == (1,1,1):
        verts = (
            Vec3(-.5,-.5,-.5), Vec3(.5,-.5,-.5), Vec3(.5,.5,-.5), Vec3(-.5,.5,-.5),
            Vec3(-.5,-.5,.5),  Vec3(.5,-.5,.5),  Vec3(.5,.5,.5), Vec3(-.5,.5,.5)
            )

        tris = (
            (0,1,2,3), (5,4,7,6),   # forward, back
            (3,2,6,7), (4,5,1,0),   # up, down
            (1,5,6,2), (4,0,3,7)    # right, left
            )
        cube = Mesh(verts, tris, mode=mode, **kwargs)

    else:
        w,h,d = subdivisions
        e = Entity()

        front =  Entity(parent=e, model=Plane((w,h)), z=-.5, rotation_x=-90)
        back =   Entity(parent=e, model=Plane((w,h)), z=.5, rotation_x=90)
        top =    Entity(parent=e, model=Plane((w,d)), y=.5)
        bottom = Entity(parent=e, model=Plane((w,d)), y=-.5, rotation_x=-180)
        right =  Entity(parent=e, model=Plane((d,h)), x=.5, rotation_z=90)
        left =   Entity(parent=e, model=Plane((d,h)), x=-.5, rotation_z=-90)

        cube = e.combine()
        cube.mode = mode
        cube.generate()
        destroy(e)

    return cube


if __name__ == '__main__':
    app = Ursina()

    e = Entity(model=Cube(subdivisions=(3,3,3), mode='line'), color=color.red)
    e = Entity(model=Cube(subdivisions=(1,1,1), mode='line'), color=color.green, x=2)

    _ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    app.run()
