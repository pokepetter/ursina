from ursina import *
from panda3d.core import GeomVertexReader, GeomVertexWriter, GeomVertexRewriter
import numpy as np


class RadiosityTest(Entity):

    def __init__(self):

        super().__init__()
        self.model = 'radiosity_test'
        # self.texture = 'project_browser_bg'
        self.scale *= 4
        player = FirstPersonController()

        # self.vertices_colored = 0
        #
        geomNodeCollection = self.model.findAllMatches('**/+GeomNode')
        for nodePath in geomNodeCollection:
            geomNode = nodePath.node()
            for i in range(geomNode.getNumGeoms()):
                # geom = geomNode.getGeom(i)      # read
                geom = geomNode.modifyGeom(i)
                # vdata = geom.getVertexData()
                vdata = geom.modifyVertexData()

                vertex = GeomVertexReader(vdata, 'vertex')
                vert_color = GeomVertexReader(vdata, 'color')
                print(vert_color)
                normal = GeomVertexReader(vdata, 'normal')
                new_color = GeomVertexWriter(vdata, 'color')

                verts = list()
                while not vertex.isAtEnd():
                    v = vertex.getData3f()
                    verts.append(v)
                    n = normal.getData3f()
                    try:
                        c = vert_color.getData4f()
                        if c == color.yellow:
                            light_position = v
                        #     light_normal = n
                    except:
                        pass
                print(len(verts))

                vertex = GeomVertexReader(vdata, 'vertex')
                # print(vertex)
                while not vertex.isAtEnd():
                    v = vertex.getData3f()
                    n = normal.getData3f()
                    try:
                        c = vert_color.getData4f()
                        if c != color.yellow:
                            # if n[0] > .5:
                            dist = distance(light_position, v)
                            new_color.setData4f(color.color(0, 0, 1-dist/2))
                            # new_color.setData4f(color.rgba(n[0], n[1], n[2]))
                            # break_outer = False
                            # temp_point = v
                            # for i in range(1):
                            #     if break_outer:
                            #         break
                            #
                            #     temp_point = (temp_point[0] + n[0], temp_point[1] + n[1], temp_point[2] + n[2])
                            #     # if distance(temp_point, light_position) < i * i * .2:
                            #     #     new_color.setData4f(color.color(60, 1, i/10 , 1))
                            #     #     break
                            #     for p in verts:
                            #         dist = distance(temp_point, p)
                            #         if dist < .01:
                            #             print('hit self')
                            #             continue
                            #         elif dist < .5:
                            #             print('hit after', i)
                            #             break
                            #             break_outer = True
                                # print('ignore')
                    except:
                        pass


class FirstPersonController(Entity):

    def __init__(self):
        super().__init__()
        self.speed = .1

        cursor = Panel()
        cursor.color = color.light_gray
        cursor.scale *= .008
        cursor.rotation_z = 45
        if not scene.editor:
            self.start()


    def start(self):
        self.position = (0, 2, 1)
        camera.parent = self
        camera.position = (0,0,0)
        camera.rotation = (0,0,0)
        camera.fov = 90
        mouse.locked = True


    def update(self):
        # print(self.left)
        self.position += self.right * held_keys['d'] * self.speed
        self.position += self.forward * held_keys['w'] * self.speed
        self.position += self.left * held_keys['a'] * self.speed
        self.position += self.back * held_keys['s'] * self.speed
        self.position += self.down * held_keys['q'] * self.speed
        self.position += self.up * held_keys['e'] * self.speed

        self.rotation_y += mouse.velocity[0] * 20
        camera.rotation_x -= mouse.velocity[1] * 20
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)




if __name__ == '__main__':
    app = main.Ursina()
    # load_scene('minecraft_clone')
    s = RadiosityTest()
    app.run()
