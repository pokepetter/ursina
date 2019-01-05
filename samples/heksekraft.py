from ursina import *


class MinecraftClone(Entity):

    def __init__(self):
        super().__init__()
        c = Cylinder(6, height=1, start=-.5)
        # print(c.vertices)
        # colors = list()
        # for i in range(6, len(c.vertices)):
        #     colors.append(color.green)
        # c.colors = colors
        # c.generate()
        c.write_bam_file('hexagon.bam')

        # print(Cylinder(6, height=.5).recipe)
        # Plane(100)
        # size = 512
        size = 4
        verts = list()
        for z in range(size):
            for x in range(size):
                for y in range(1):
                    voxel = Entity(
                        parent = self,
                        name = 'voxel',
                        # model = Cylinder(6, height=.5),
                        model = 'hexagon',
                        # model = c,
                        origin_y = -.5,
                        # collider = 'mesh',
                        # collider = 'sphere',
                        # collider = BoxCollider(position=(0,0,0), size=(1,1,1)),
                        color = lerp(lerp(color.brown, color.dark_gray, .5), color.random_color(), .1),
                        index = (x,y,z),
                        position=(x*.8660025,y,z*.75)
                        )
                    voxel.collider = MeshCollider(voxel, mesh=c, center=-voxel.origin)
                    top = Entity(parent=voxel, model='hexagon', y=1, scale_y=.01)
                    top.color = lerp(color.lime, color.random_color(), .2)
                    # voxel.collider.visible = True

                    if z%2 == 0:
                        voxel.x += .5*.8660025

                    # voxel.scale_y = random.uniform(0,1)
                    # verts.append((x/5, random.uniform(0,1)/5, z/5))
        # colors = [color.random_color() for e in verts]
        # Entity(model=Mesh(vertices=verts, thickness=100, colors=colors, mode='point'), texture='brick')
        sky = Sky()
        from panda3d.core import DirectionalLight
        dlight = DirectionalLight('my dlight')
        dlnp = render.attachNewNode(dlight)
        dlnp.lookAt(Vec3(5,6,5))
        player = FirstPersonController()

class Magician(Entity):
    def update(self):
        if mouse.left and mouse.hovered_entity:
            mouse.hovered_entity.scale_y += .1
        if mouse.right and mouse.hovered_entity:
            mouse.hovered_entity.scale_y -= .1
Magician()

class FirstPersonController(Entity):

    def __init__(self):
        super().__init__()
        self.speed = .025

        self.i = 0
        self.update_interval = 30

        self.cursor = Panel()
        self.cursor.color = color.pink
        self.cursor.scale *= .008
        self.cursor.rotation_z = 45

        self.graphics = Entity(
            name = 'player_graphics',
            parent = self,
            model = 'cube',
            origin = (0, -.5, 0),
            scale = (1, 1.8, 1),
            )

        self.arrow = Entity(
            parent = self.graphics,
            model = 'cube',
            color = color.blue,
            position = (0, .5, .5),
            scale = (.1, .1, .5)
            )

        camera.parent = self
        self.position = (0, 1, 1)
        camera.rotation = (0,0,0)
        camera.position = (0,1,0)
        camera.fov = 90
        mouse.locked = True


    def update(self):
        if self.i < self.update_interval:
            self.i += 1
            return

        self.direction = (
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            )

        if not raycast(self.world_position + self.up, self.direction, 1).hit:
            self.position += self.direction * self.speed

        self.rotation_y += mouse.velocity[0] * 40
        camera.rotation_x -= mouse.velocity[1] * 40
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)



if __name__ == '__main__':
    app = Ursina()
    # window.size = (450, 450/window.aspect_ratio)
    # window.center_on_screen()
    MinecraftClone()
    # vr = VideoRecorder(name='minecraft_clone')
    # invoke(setattr, vr, 'recording', True, delay=1)
    app.run()
