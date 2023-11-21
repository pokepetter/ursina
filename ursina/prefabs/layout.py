from ursina import *


class Layout(Entity):
    def __init__(self, color=color.gray, z=999, **kwargs):
        super().__init__(model=Quad(radius=.0), color=color, z=z, **kwargs)
        self.parent = camera.ui
        self.color = self.color.tint(-.05)
        self.wdw = window.size.x
        self.wdh = window.size.y
        self.qoef = 100

        if 'color' in kwargs:
            setattr(self, 'color', kwargs['color'])

        if "side" in kwargs:
            print(kwargs['side'])
            if kwargs["side"] == "TOP" or kwargs["side"] == "top":
                self.position = window.top
                self.scale = (self.wdw, 25/self.qoef)
            elif kwargs["side"] == "LEFT" or kwargs["side"] == "left":
                self.position = window.left
                self.scale = (25/self.qoef, self.wdh)
            elif kwargs["side"] == "BOTTOM" or kwargs["side"] == "bottom":
                self.position = window.bottom
                self.scale = (self.wdw, 25/self.qoef)
            elif kwargs["side"] == "RIGHT" or kwargs["side"] == "right":
                self.position = window.right
                self.scale = (25/self.qoef, self.wdh)
            else:
                print("Layout can't pack")


if __name__ == "__main__":
    app = Ursina()
    window.fullscreen = False
    window.borderless = False
    window.exit_button.enabled = False
    window.fps_counter.enabled = False

    # layout_top = Layout(side="TOP", color=color.black50)

    layout_left = Layout(side="LEFT", color=color.red)

    # layout_bottom = Layout(side="BOTTOM", color=color.blue)

    # layout_right = Layout(side="RIGHT", color=color.green)

    print(window.size)

    app.run()
