from ursina import *


class Layout(Entity):
    def __init__(self, color=color.gray, z=999, **kwargs):
        super().__init__(model=Quad(radius=.0), color=color, z=z, **kwargs)
        self.parent = camera.ui
        self.color = self.color.tint(-.05)
        self.postion = (0, 5)
        self.scale = (10, 5)
        self.wdw = window.size.x
        self.wdh = window.size.y

        if 'color' in kwargs:
            setattr(self, 'color', kwargs['color'])

        if "side" in kwargs:
            print(kwargs['side'])
            if kwargs["side"] == "TOP":
                self.position = window.top
                self.scale = (self.wdw, 0.25)
            elif kwargs["side"] == "LEFT":
                self.position = window.left
                self.scale = (0.25, self.wdh)
            elif kwargs["side"] == "BOTTOM":
                self.position = window.bottom
                self.scale = (self.wdw, 0.25)
            elif kwargs["side"] == "RIGHT":
                self.position = window.right
                self.scale = (0.25, self.wdh)
            else:
                print("Layout can't pack")


if __name__ == "__main__":
    app = Ursina()
    window.fullscreen = False
    window.borderless = False
    window.exit_button.enabled = False
    window.fps_counter.enabled = False

    layout_top = Layout(side="TOP", color=color.black50)

    layout_left = Layout(side="LEFT", color=color.red)

    layout_bottom = Layout(side="BOTTOM", color=color.blue)

    layout_right = Layout(side="RIGHT", color=color.green)

    print(window.size)

    app.run()
