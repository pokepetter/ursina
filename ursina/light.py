from panda3d.core import NodePath
from panda3d.core import DirectionalLight, AmbientLight, PointLight, Spotlight
from panda3d.core import PerspectiveLens
from ursina.vec3 import Vec3
from ursina import scene
from ursina import color


LightTypes = ('ambient', 'directional', 'point', 'spot')

class Light():

    def __init__(self, **kwargs):

        self.type = 'ambient'              # ambient or directional for now
        self.color = color.rgb(0.3,0.3,0.3,1)        # a modest amount of full-spectrum light
        self.direction = Vec3(-1,-1,-1)         # shining down from top-right corner, behind camera
        self.position = Vec3(0,0,0)
        self.fov = 60
        self.node = None


        for key, value in kwargs.items():

            if key == 'type':
                if value in LightTypes:
                    self.type = value
                else:
                    print(f"ERR Light type is not in {LightTypes}")
            elif key == 'color':
                self.color = value
            elif key == 'direction' and self.type not in ('ambient','point'):
                self.direction = value
            elif key == 'position' and self.type!='ambient':
                self.position = value
            elif key == "fov" and self.type=='spot':
                self.fov = value
            else:
                print(f"ERR {key} is not a valid keyword for light type {self.type}")

            scene.lights.append(self)   # light added for all subsequent entities

            if self.type == 'ambient':
                self.light = AmbientLight('ambientLight')
                self.light.setColor(self.color)
                self.node = scene.attachNewNode(self.light)

            elif self.type == 'directional':
                self.light = DirectionalLight('directionalLight')
                self.light.setColor(self.color)
                self.node = scene.attachNewNode(self.light)
                # This light should be facing straight down, but clearly it isn't.
                self.node.setHpr(self.direction)  # convert vector to Hpr (in degrees!?) first

            elif self.type == 'point':
                self.light = PointLight('pointLight')
                self.light.setColor(self.color)
                self.node = scene.attachNewNode(self.light)
                self.node.setPos(self.position)

            elif self.type == 'spot':
                self.light = Spotlight('spotlight')
                self.light.setColor(self.color)
                lens = PerspectiveLens()
                lens.setFov(self.fov)
                self.light.setLens(lens)
                self.node = scene.attachNewNode(self.light)
                self.node.setPos(self.position)
                self.node.setHpr(self.direction)


if __name__ == '__main__':
    from ursina import *

    app = Ursina()  # create the game

    cubes = []

    # best to paste up text BEFORE you mess with the lights
    Text(origin=(4,-18), text="default lighting")
    Text(origin=(.8,-4), text="replace with dimmer ambient for these three cubes")
    Text(origin=(.9,11), text="also add a bit of directional for these three cubes")

    cubes.append(Entity(model='cube', color=color.red, position=(-4,3,0)))
    cubes.append(Entity(model='cube', color=color.green, position=(0,3,0)))
    cubes.append(Entity(model='cube', color=color.blue, position=(4,3,0)))

    # add a light for all subsequent entities
    Light(type='ambient', color=(0.3,0.3,0.3,1))  # full spectrum

    cubes.append(Entity(model='cube', color=color.red, position=(-4,0,0)))
    cubes.append(Entity(model='cube', color=color.green, position=(0,0,0)))
    cubes.append(Entity(model='cube', color=color.blue, position=(4,0,0)))

    # add a light for all subsequent entities
    Light(type='directional', color=(0.3,0.3,0.3,1), direction=(1,1,1))  # dim full spectrum

    cubes.append(Entity(model='cube', color=color.red, position=(-4,-3,0)))
    cubes.append(Entity(model='cube', color=color.green, position=(0,-3,0)))
    cubes.append(Entity(model='cube', color=color.blue, position=(4,-3,0)))

    def update():
        for i in cubes:
            i.rotation_x += .3
            i.rotation_y += .3
            i.rotation_z += .2

    app.run()   # opens a window and starts the game.
