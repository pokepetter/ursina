import sys
sys.path.append("..")
from ursina import *
import asyncio

class Generator_1(Entity):

    def __init__(self):
        super().__init__()
        # self.position_noise = .3
        self.parent = render
        self.name = 'yolo'
        print('--------fffffff------')

        # for z in range(64):
        #     for x in range(64):
        #         for y in range(8):
        #             self.cube = Entity()
        #             self.cube.model = 'cube'
        #             self.cube.color = color.color(x * 30, 1, (z + 1) / 10)
        #             self.cube.position = (x, y, z)


    def input(self, key):
        if key == 'g':
            print('generate stuff')
            loop = asyncio.get_event_loop()
            # loop.run_until_complete(self.generate())
            self.generate()
            loop.close()


    async def generate(self):
        self.cubes = list()

        for z in range(3):
            for x in range(3):
                for y in range(1):
                    self.cube = Entity()
                    self.cube.enabled = False
                    self.cube.model = 'cube'
                    # self.cube.parent = render
                    # self.cube.color = color.color(x * 30, 1, (z + 1) / 10)
                    self.cube.color = color.color(90, .75, .5 + (y / 16) + random.uniform(0, .1))
                    self.cube.position = (x, y, z)
                    self.cubes.append(self.cube)

                    print(x)
                    # await asyncio.sleep(0.2)

        for c in self.cubes:
            c.enabled = True
            await asyncio.sleep(0.5)

                    # placeholder = render.attachNewNode('placeholder')
                    # placeholder.setPos(x, z, y)
                    # block.instanceTo(placeholder)


# dancer = Actor.Actor("chorus-line-dancer.egg", {"kick":"kick.egg"})
# dancer.loop("kick")
# dancer.setPos(0,0,0)
# for i in range(50):
#   placeholder = render.attachNewNode("Dancer-Placeholder")
#   placeholder.setPos(i*5, 0, 0)
#   dancer.instanceTo(placeholder)

from threading import Thread
from time import sleep as wait


class R(Thread):

    def __init__(self):
        print(dir(self))


    def lerp(self):
        # self.i = 0

        for i in range(8):
            print(i)
            wait(.2)

        # self.lerp()

# r = R()
# r.lerp()
