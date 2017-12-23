import sys
sys.path.append('..')
from pandaeditor import *


class PuzzleGame(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'puzzle_game'

        # for z in range(5):
        #     for x in range(5):
        #         voxel = Voxel()
        #         voxel.parent = self
        #         voxel.position = (x, 0, z)
        self.load_level('white_cube')

        player = FirstPersonController()
        player.parent = self

    def load_level(self, name):
        from PIL import Image
        im = Image.open(application.internal_texture_folder + name + '.png')
        pix = im.load()
        print (im.size)
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                print('color:', pix[x,y])


class Voxel(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'voxel'
        self.model = 'cube'
        self.origin = (0, .5, 0)
        self.scale_y = 8
        self.collider = 'box'
        self.texture = 'white_cube'
        self.color = color.color(0, 0, random.uniform(.9, 1.0))


    def input(self, key):
        if self.hovered:
            if key == 'left mouse down' and self.y < 7:
                self.y += 1

            if key == 'right mouse down' and self.y > 0:
                self.y -= 1


class FirstPersonController(Entity):

    def __init__(self):
        super().__init__()
        self.speed = .1

        cursor = Panel()
        cursor.color = color.dark_gray
        cursor.scale *= .01
        cursor.rotation_z = 45


    def start(self):
        self.position = (0, 2, 1)
        camera.parent = self
        camera.position = (0,0,0)
        camera.rotation = (0,0,0)
        camera.fov = 90
        mouse.locked = True


    def update(self, dt):


        self.position += self.right * held_keys['d'] * self.speed
        self.position += self.forward * held_keys['w'] * self.speed
        self.position += self.left * held_keys['a'] * self.speed
        self.position += self.back * held_keys['s'] * self.speed

        self.rotation_y += mouse.velocity[0] * 20
        camera.rotation_x -= mouse.velocity[1] * 20
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)


if __name__ == '__main__':
    app = main.PandaEditor()
    scene.entity = PuzzleGame()
    app.run()
