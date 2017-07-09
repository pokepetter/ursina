from pandaeditor import *

global screen_width
global screen_height
global aspect_ratio


class Button():

    def __init__(self):
        self.target = None
        self.ui = None
        self.color = color.black
        self.hovered = False


    def set_up(self):
        # pass
        self.target.collision = True
        self.target.model.showTightBounds()
        # print(self.target.model.calcTightBounds())
        # collider_position = self.target.model.getPos(self.ui.target.node_path)
        # # collider_position = (self.target.position[0] + (offset[0] / self.target.scale[0]),
        # #                     self.target.position[1] + (offset[1] / self.target.scale[1]),
        # #                     self.target.position[2] + (offset[2] / self.target.scale[2]))
        # collider_position = self.target.model.getPos(self.ui.target.model)
        # collider_position = self.target.node_path.getPos(camera.render)
        # print(collider_position)
        #
        # self.target.collider = (collider_position, (0,0,0), self.target.model.getScale(self.ui.target.model))

        # box = CollisionBox(self.target.position, 1, 1, 1)
        # self.target.collider = avatar.attachNewNode(CollisionNode('cnode'))
        # self.target.collider.node().addSolid(box)
        # cnodePath.show()

        # temp_parent = self.target.parent
        # self.target.parent = self.ui.target.node_path
        # self.target.collider = True
        # print(self.target.collider)
        # self.target.parent = temp_parent

        self.highlight_color = tuple(x + 0.1 for x in self.color)
        self.pressed_color = tuple(x - 0.2 for x in self.color)
        self.target.model.setColorScale(self.color)


        node = debug.draw_box_collider(self.target.collider)
        # self.ui.target.node_path.attachNewNode(node)


    def input(self, key):
        if key == 'left mouse down':
            if mouse.hovered_thing == self.target:
                self.target.model.setColorScale(self.pressed_color)
        if key == 'left mouse up':
            if self.hovered:
                self.target.model.setColorScale(self.highlight_color)
            else:
                self.target.model.setColorScale(self.color)


    def update(self, dt):
        if self.target.collider:
            pos3d = Point3()
            nearPoint = Point3()
            farPoint = Point3()
            camera.lens.extrude(mouse.position, nearPoint, farPoint)
            screen_depth = int(farPoint[1] - nearPoint[1])
            if not self.hovered:
                for i in range(screen_depth):
                    pos = nearPoint + (farPoint * i / screen_depth)
                    if collision.point_inside_thing(pos, thing):
                        self.target.model.setColorScale(self.highlight_color)
                        print('hovered:', self.hovered)
                        self.hovered = True
                        break


        if not self.hovered:
            if collision.point_inside_thing_2d(mouse_2d, self.target):
                # enter
                self.target.model.setColorScale(self.highlight_color)
                self.hovered = True
        else:
            if not collision.point_inside_thing_2d(mouse_2d, self.target):
                # exit
                self.target.model.setColorScale(self.color)
                self.hovered = False
