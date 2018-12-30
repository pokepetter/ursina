from ursina import *


class AutoStairs(Entity):
    def __init__(self, height=1, **kwargs):
        super().__init__(**kwargs)
        # self.box = Entity(model='cube', scale=(1,height,.1), origin=(0,.5,0))
        random.seed(0)
        pause_every = 16
        pause_size = 1

        step_height = .1
        step_depth = .15
        steps = math.ceil(height/step_height)
        rail_height = .5


        z = 0
        for i in range(steps):

            step = Entity(
                parent = self,
                # model = 'cube',
                model = Mesh(
                    vertices=(
                        (.5,.5,-.5), (.5,.5,.5), (-.5,.5,.5),
                        (-.5,.5,-.5),(.5,-.5,.5),(-.5,-.5,.5)),
                    triangles=(0,1,2, 0,2,3, 4,5,1, 1,5,2),
                    mode='triangle'
                    ),
                origin = (0,.5,-.5),
                position = (0, -i*step_height, z),
                scale = (1, step_height, step_depth),
                color = color.tint(color.color(0,0,.4), random.uniform(-.05,.05))
                # color = color.color(i*20, 1, .7, .2)
                )

            z += step_depth

            if pause_every and i % pause_every == 0 and i > 0:
                z += pause_size - step_depth
                step.scale_z = pause_size

        # rail poles
        rail_poles = list()
        for i, step in enumerate(self.children):
            for j in range(int(step.scale_z // step_depth)):
                rail_pole = Entity(
                    parent = step,
                    model = 'cube',
                    origin = (0,-.5,0),
                    x = .45,
                    world_z = step.world_z + (j * step_depth * self.scale_z) - (step_depth/2),
                    color = color.dark_gray,
                    world_scale = (.05, rail_height, .05)
                    )
                rail_pole.world_z += step_depth
                rail_poles.append(rail_pole)
                rail_pole_2 = duplicate(rail_pole)
                rail_pole_2.x = -.45


        if len(self.children) == 0:
            return

        verts = list()
        last_step = self.children[-1]
        for step in reversed(self.children):
            verts.append((0, last_step.y-step_height, 0))
            verts.append(step.position + Vec3(0,-step.scale_y,step.scale_z))
            verts.append(step.position + Vec3(0,0,step.scale_z))

            verts.append((0, last_step.y-step_height, 0))
            verts.append(step.position + Vec3(0,0,step.scale_z))
            verts.append(step.position)


        side = Entity(
            parent = self,
            model = Mesh(vertices=verts, mode='triangle', thickness=10),
            x = .5,
            color = color.color(0,0,.35)
            )

        side_2 = duplicate(side)
        side_2.x *= -1
        side_2.flip_faces()

        path = list()
        path.append(rail_poles[0].world_position + (0,rail_height,-.2)) # first
        for rp in rail_poles:
            path.append(rp.world_position + Vec3(0,rail_height,0))
        path.append(rail_poles[len(rail_poles)-1].world_position + (self.forward * .1) + (self.up * (rail_height-.1))) # last

        railing = Entity(model=Prismatoid(path=path, thicknesses=((.1,.05),)), color=color.orange, world_parent=self)
        railing_2 = Entity(model=Prismatoid(path=path, thicknesses=((.1,.05),)), color=color.orange, world_parent=self)
        railing_2.scale_x *= -1
        railing_2.flip_faces()

        ground_collider = primitives.GreenCube(
            parent = self,
            origin = (0,.5,-.5),
            scale_y = .8,
            world_z = step_depth/2
            )
        ground_collider.look_at(last_step)
        ground_collider.scale_z = distance(ground_collider, Vec3(last_step.position) + (Vec3(0,-step_height,step_depth)*2))


        top_collider = primitives.BlueCube(
            parent = self,
            origin = (0,.5,-.5),
            scale_z = step_depth/2,
            )

        rail_collider = duplicate(ground_collider)
        rail_collider.scale_x = .1
        rail_collider.x = .5 - (.1/2)
        rail_collider.scale_y = rail_height * .9
        rail_collider.scale_z = distance(rail_collider, Vec3(last_step.position) - (Vec3(0,-step_height,step_depth)))
        rail_collider.origin_y = -.5

        rail_start = primitives.RedCube(
            x = .5 - (.1/2),
            origin = (0, -.5, -.5),
            scale = (.1, rail_height, step_depth*2)
            )
        rail_end = duplicate(rail_start)
        rail_end.position = (rail_end.x, -steps*step_height, steps*step_depth)
        rail_end.origin_z = .5


if __name__ == '__main__':
    app = Ursina()

    class AutoStairsTester(Entity):
        def __init__(self):
            super().__init__()
            self.height = 1
            self.stair = AutoStairs(height=self.height)

        def input(self, key):
            if key == 'e':
                self.height += .1
                destroy(self.stair)
                self.stair = AutoStairs(height=self.height)
            if key == 'q':
                self.height -= .1
                destroy(self.stair)
                self.stair = AutoStairs(height=self.height)
    # AutoStairs()
    Sky()
    AutoStairsTester()
    EditorCamera()
    camera.orthographic = True
    camera.fov = 2
    camera.position = Vec3(10, 5, 5) * 1.5
    # camera.position = Vec3(10, 0, 0)
    camera.look_at((0,0,0))
    origin = Entity(model=Sphere(), color=color.red, scale=(.01,.01,.01))
    app.run()
