from ursina import *

'''
nineslice mesh:

11-10--15--14
|   |   |   |
8---9--12--13
|   |   |   |
3---2---7---6
|   |   |   |
0---1---4---5

'''


class NineSlice(Mesh):
    def __init__(self, entity_scale=Vec3.one, scale_multiplier=1):
        verts = [Vec3(*e,0)*scale_multiplier for e in (
            (-.5,-.5), (0,-.5), (0,0), (-.5,0),
            (0,-.5), (.5,-.5), (.5,-0), (0,-0),
            (-.5,0), (-0,0), (-0,.5), (-.5,.5),
            (0,0), (.5,0), (.5,.5), (0,.5),
            )]

        offset = (entity_scale - Vec3.one)
        for i in range(0,4):
            verts[i] -= offset * .5
            verts[i] *= Vec3.one / entity_scale
        for i in range(4,8):
            verts[i] += offset * Vec3(1,-1,1) * .5
            verts[i] *= Vec3.one / entity_scale
        for i in range(8,11):
            verts[i] += offset * Vec3(-1,1,1) * .5
            verts[i] *= Vec3.one / entity_scale
        for i in range(12,16):
            verts[i] += offset * .5
            verts[i] *= Vec3.one / entity_scale

        super().__init__(
            vertices=verts,
            triangles=(
                (0,1,2,3),
                (1,4,7,2),
                (4,5,6,7),
                (3,2,9,8,),
                (2,7,12,9),
                (7,6,13,12),
                (8,9,10,11),
                (9,12,15,10),
                (12,13,14,15)
                ),
            uvs=(
                (0,0), (.5,0), (.5,.5), (0,.5),
                (.5,0), (1,0), (1,.5), (.5,.5),
                (0,.5), (.5,.5), (.5,1), (0,1),
                (.5,.5), (1,.5), (1,1), (.5,1)
                ),
            )



if __name__ == '__main__':
    app = Ursina()
    m = NineSlice(entity_scale=Vec3(2,1,1),
        # scale_multiplier=1.4,   # account for whitespace and drop shadow in the texture
        )

    window.color = color._240

    Entity(parent=camera.ui, model='wireframe_quad', scale=Vec2(2,1)*.1, color=color.red)
    for i, (nineslice_texture, scale_multiplier) in enumerate(
        zip(
            ('nineslice_rainbow', 'nineslice_double', 'circle'),
            (1.4, 1.4, 1), strict=True
        )):
        b = Draggable(
            model=NineSlice(entity_scale=Vec3(2,1,1), scale_multiplier=scale_multiplier),
            scale=Vec2(2,1)*.1,
            texture=nineslice_texture,
            text='Next',
            color=color.white,
            text_color=color.dark_gray,
            text_origin=(0,0),
            highlight_color=hsv(210,.1,1),
            pressed_scale=.9,
            pressed_color=hsv(180,.2,.7),
            # wireframe=True,
            y=-i*.2
            )

    # button1 = Entity(text="Hi !!", model=NineSlice(0.2, 0.3), position=(-0.2, -0.3), texture="nine_sliced", color=color.white)
    # button2 = Entity(text="Hello !!!", model=NineSlice(0.5, 0.3), position=(0.2, -0.3), texture="nine_sliced", color=color.white)
    # button3 = Entity(text="As you can see, the texture goes \nwell for every button size.", model=NineSlice(0.4, 0.4), position=(0, 0.1), texture="nine_sliced", color=color.white)
    EditorCamera()
    app.run()