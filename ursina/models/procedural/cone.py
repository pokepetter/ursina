from ursina import *


class Cone(Mesh):
    def __init__(self, resolution=4, radius=.5, height=1, direction=(0,1,0), add_bottom=True, mode='triangle', **kwargs):
        origin = Entity()
        point = Entity(parent=origin)

        axis_index = direction.index(1)
        right = axis_index+1
        if right >= 3:
            right = 0
        setattr(point, ('x', 'y', 'z')[right], radius)

        rot_axis = 'rotation_' + ('x', 'y', 'z')[axis_index]

        verts = list()
        for i in range(resolution):
            verts.append(point.world_position) # outer point
            if add_bottom:
                verts.append((0,0,0)) #center point

            setattr(origin, rot_axis, getattr(origin, rot_axis) - 360/resolution)
            verts.append(point.world_position) # next outer point

            if add_bottom:
                setattr(origin, rot_axis, getattr(origin, rot_axis) - 360/resolution)

            verts.append((height*direction[0], height*direction[1], height*direction[2])) # spike point

            if add_bottom:
                verts.append(point.world_position)
                setattr(origin, rot_axis, getattr(origin, rot_axis) - 360/resolution)
                verts.append(point.world_position)

        destroy(origin)
        destroy(point)

        super().__init__(vertices=verts, mode=mode, **kwargs)


if __name__ == '__main__':
    app = Ursina()
    # Entity(model=Cone(8), color=color.color(60,1,1,.3))
    Entity(model=Cone(8, direction=(0,1,0)), color=color.color(60,1,1,.3))
    origin = Entity(model='quad', color=color.orange, scale=(.05, .05))
    ed = EditorCamera(rotation_speed = 200, panning_speed=200)
    app.run()
