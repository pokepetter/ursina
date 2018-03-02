from pandaeditor import *
from PIL import Image


class Paper(Entity):
    def __init__(self):
        super().__init__()

        self.name = 'paper'
        self.scale *= 7
        self.model = 'quad'
        self.collider = 'box'
        self.width = 0
        self.height = 0


    def start(self):
        self.new()

    def new(self, width=256, height=256):
        self.width = width
        self.height = height

        self.img = Image.new('RGBA', (256,256), (255, 255, 255))
        self.brush = Image.open("brush.png")

        texture = Texture()
        texture.setup2dTexture(width, height, Texture.TUnsignedByte, Texture.FRgba)
        texture.setRamImageAs(self.img.tobytes(), "RGBA")
        self.texture = texture

        self.img.paste(self.brush, (0, 0), self.brush)
        self.texture.setRamImageAs(self.img.tobytes(), "RGBA")


    def update(self, dt):
        if held_keys['space']:
            camera.x -= mouse.velocity[0] * 10
            camera.y -= mouse.velocity[1] * 10

        if mouse.left and mouse.point:
            self.tex_x = int((mouse.point[0] + .5) * self.width)
            self.tex_y = int((mouse.point[1] + .5) * self.height)

            print(self.tex_x, self.tex_y)
            self.img.paste(self.brush, (self.tex_x, self.tex_y), self.brush)
            self.texture.setRamImageAs(self.img.tobytes(), "RGBA")


app = PandaEditor()
cursor = Cursor()
paper = Paper()
app.run()
