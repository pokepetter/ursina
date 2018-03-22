from pandaeditor import *
from PIL import Image, ImageChops
# import opencv-python as ocv
import numpy


class Paper(Entity):
    def __init__(self):
        super().__init__()

        self.name = 'paper'
        self.scale *= 7
        self.model = 'quad'
        self.collider = 'box'

        self.prev_pos = None
        self.width = 0
        self.height = 0
        self.i = 0
        # self.pressure = .1

        self.brush = Image.open("brush.png")
        self.brush_color = (int(color.lime[0] * 255), int(color.lime[1] * 255), int(color.lime[2] * 255))
        tint = Image.new("RGBA", (self.brush.width, self.brush.height), self.brush_color)
        self.brush = ImageChops.multiply(self.brush, tint)


    def start(self):
        self.new()

    def new(self, width=1024, height=1024):
        self.width = width
        self.height = height

        self.img = Image.new('RGBA', (width, height), (255, 255, 255))

        texture = Texture()
        texture.setup2dTexture(width, height, Texture.TUnsignedByte, Texture.FRgba)
        texture.setRamImageAs(self.img.tobytes(), "RGBA")
        self.texture = texture

        self.img.paste(self.brush, (0, 0), self.brush)
        self.texture.setRamImageAs(self.img.tobytes(), "RGBA")

    def input(self, key):
        if key == 'left mouse up':
            self.prev_pos = None

    def update(self, dt):
        # if mouse.left and self. pressure < 2:
        #     self.pressure += .1

        if held_keys['space']:
            camera.x -= mouse.velocity[0] * 10
            camera.y -= mouse.velocity[1] * 10

        if mouse.left and mouse.point:
            self.tex_x = int((mouse.point[0] + .5) * self.width)
            self.tex_y = int((mouse.point[1] + .5) * self.height)
            self.prev_point = (self.tex_x, self.tex_y)



            # print(self.tex_x, self.tex_y)
            # self.resized_brush = self.brush.thumbnail(
            #     (int(8), int(8)),
            #     Image.ANTIALIAS)

            # self.resized_brush = self.brush.resize((int(self.brush.width * self.pressure), int(self.brush.height * self.pressure)), Image.ANTIALIAS)

            # if self.pressure < .01:
            #     return
            self.img.paste(
                self.brush,
                (int(self.tex_x - (self.brush.size[0] / 2)),
                int(self.tex_y - (self.brush.size[1] / 2))),
                self.brush)

            # if self.prev_pos:
            #     # dist = distance(Vec3(self.tex_x, self.tex_y, 0), self.prev_pos)
            #     # print('delta pos:', dist)
            #     dx = self.tex_x - self.prev_pos[0]
            #     # dy = self.tex_y - self.prev_pos[1]
            #     # steps = max(dx, dy)
            #     steps = int(dx/20)
            #     print(steps)
            #
            #     for i in range(steps):
            #         self.img.paste(
            #             self.brush,
            #             (int(self.tex_x - (self.brush.size[0] / 2) + (i*20)),
            #             int(self.tex_y - (self.brush.size[1] / 2))),
            #             self.brush)


                # for i in range(distance):
                #     paste_pos =

            self.prev_pos = Vec3(self.tex_x, self.tex_y, 0)

            self.i += 1
            if self.i > 2:  # update image less often to reduce lag.
                self.texture.setRamImageAs(self.img.tobytes(), "RGBA")
                self.i = 0


app = PandaEditor()
cursor = Cursor()
paper = Paper()
app.run()
