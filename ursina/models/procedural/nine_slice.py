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
    def __init__(self, entity_scale=Vec2.one, radius=.5, scale_multiplier=1):
        verts = [Vec2(*e)*scale_multiplier for e in (
            (-.5,-.5), (-.5,-.5), (-.5,-.5), (-.5,-.5),
            (.5,-.5), (.5,-.5), (.5,-.5), (.5,-.5),
            (-.5,.5), (-.5,.5), (-.5,.5), (-.5,.5),
            (.5,.5), (.5,.5), (.5,.5), (.5,.5),
            )]
        if isinstance(entity_scale, Vec3):
            entity_scale = entity_scale.xy
        elif isinstance(entity_scale, float | int):
            entity_scale = Vec2(entity_scale)
        elif isinstance(entity_scale, tuple | list):
            entity_scale = Vec2(*entity_scale)

        if entity_scale.x > entity_scale.y:
            aspect_ratio = (entity_scale.x / entity_scale.y)
            print('aspect_ratio', aspect_ratio, entity_scale)
            for idx in (1,2,9,10):
                verts[idx].x += radius / aspect_ratio
            for idx in (4,7,12,15):
                verts[idx].x -= radius / aspect_ratio
            for idx in (3,2,7,6):
                verts[idx].y += radius
            for idx in (8,9,12,13):
                verts[idx].y -= radius

        else:
            aspect_ratio = (entity_scale.y / entity_scale.x)
            for idx in (1,2,9,10):
                verts[idx].x += radius
            for idx in (4,7,12,15):
                verts[idx].x -= radius
            for idx in (3,2,7,6):
                verts[idx].y += radius / aspect_ratio
            for idx in (8,9,12,13):
                verts[idx].y -= radius / aspect_ratio


        super().__init__(
            vertices=[Vec3(*p,0) for p in verts],
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

    window.color = color._0

    Entity(parent=camera.ui, model='wireframe_quad', scale=Vec2(2,1)*.1, color=color.red)
    # for i, (nineslice_texture, scale_multiplier) in enumerate(
    #     zip(
    #         ('nineslice_rainbow', 'nineslice_double', 'circle'),
    #         (1.4, 1.4, 1), strict=True
    #     )):
    #     b = Draggable(
    #         model=NineSlice(entity_scale=Vec3(2,1,1), scale_multiplier=scale_multiplier),
    #         scale=Vec2(2,1)*.1,
    #         texture=nineslice_texture,
    #         text='Next',
    #         color=color.white,
    #         text_color=color.dark_gray,
    #         text_origin=(0,0),
    #         highlight_color=hsv(210,.1,1),
    #         pressed_scale=.9,
    #         pressed_color=hsv(180,.2,.7),
    #         # wireframe=True,
    #         y=-i*.2
    #         )

    # button1 = Entity(text="Hi !!", model=NineSlice(2, 3), scale=(.2,.3), position=(-0.2, -0.3), texture="nineslice_rainbow", color=color.white)
    button2 = Draggable(parent=scene, model=NineSlice((1,1)), scale=1, position=(0,0), origin=(-.5,-.5), texture="nineslice_rainbow", color=color.white)
    button2 = Draggable(parent=scene, model=NineSlice((2,1)), scale=(2,1), position=(0,1), origin=(-.5,-.5), texture="nineslice_rainbow", color=color.white, wireframe=False)
    button2 = Draggable(parent=scene, model=NineSlice((1,3)), scale=(1,3), position=(1,-2), origin=(-.5,-.5), texture="nineslice_rainbow", color=color.white, wireframe=False)
    button2 = Draggable(parent=scene, model=NineSlice((3,1)), scale=(3,1), position=(-2,-1), origin=(-.5,-.5), texture="nineslice_rainbow", color=color.white, wireframe=False)
    # button3 = Entity(text="As you can see, the texture goes \nwell for every button size.", model=NineSlice(0.4, 0.4), position=(0, 0.1), texture="nine_sliced", color=color.white)
    EditorCamera()
    Entity(model=Grid(8,8), scale=8)


    app.run()